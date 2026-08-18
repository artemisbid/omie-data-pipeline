from __future__ import annotations

import json
from pathlib import Path

from core.models import ExecutionMode, ExecutionStatus, RawPage, ResourceSpec, ResourceName, RunContext
from core.use_cases import PipelineServices, execute_resource
from extract.raw_store import LocalRawStore
from extract.resources import CUSTOMERS
from load.local_sink import InMemorySupabaseSink
from load.worker import LoadWorker
from transform.workers import transform_resource


class FakeExtractor:
    def __init__(self, pages: list[RawPage]):
        self.pages = pages

    def extract(self, resource, context, mode):
        return self.pages


class FakeTransformer:
    def transform(self, resource, pages):
        return transform_resource(resource, pages)


class Checkpoints:
    def __init__(self):
        self.values: dict[str, str] = {}

    def get(self, resource_name):
        return self.values.get(resource_name)

    def set(self, resource_name, checkpoint):
        self.values[resource_name] = checkpoint


class FailingLoader:
    def load(self, resource, records):
        raise RuntimeError("supabase unavailable")


def customer_page() -> RawPage:
    return RawPage(page_number=1, payload={"clientes_cadastro": [{"codigo_cliente_omie": 10, "razao_social": "A"}]})


def services_for(tmp_path: Path, loader):
    return PipelineServices(
        extractor=FakeExtractor([customer_page()]),
        raw_store=LocalRawStore(tmp_path),
        transformer=FakeTransformer(),
        loader=loader,
    )


def test_pipeline_writes_pages_manifest_and_checkpoint_only_on_success(tmp_path: Path) -> None:
    checkpoints = Checkpoints()
    services = services_for(tmp_path, LoadWorker(InMemorySupabaseSink()))
    services.checkpoints = checkpoints
    context = RunContext(run_id="run-success")

    result = execute_resource(services, CUSTOMERS, context, ExecutionMode.FULL)

    run_dir = tmp_path / "default" / "customers" / "run-success"
    assert result.status == ExecutionStatus.SUCCESS
    assert (run_dir / "pages" / "page_0001.json").exists()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "rejected.json").exists()
    assert checkpoints.values == {"customers": "10"}

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "success"


def test_partial_result_does_not_advance_checkpoint(tmp_path: Path) -> None:
    checkpoints = Checkpoints()
    services = services_for(tmp_path, LoadWorker(InMemorySupabaseSink()))
    services.checkpoints = checkpoints
    services.extractor = FakeExtractor(
        [RawPage(page_number=1, payload={"clientes_cadastro": [{"codigo_cliente_omie": 1}, {"razao_social": "bad"}]})]
    )

    result = execute_resource(services, CUSTOMERS, RunContext(run_id="run-partial"), ExecutionMode.FULL)

    assert result.status == ExecutionStatus.PARTIAL
    assert checkpoints.values == {}


def test_loader_failure_writes_failed_manifest_without_checkpoint(tmp_path: Path) -> None:
    checkpoints = Checkpoints()
    services = services_for(tmp_path, FailingLoader())
    services.checkpoints = checkpoints

    result = execute_resource(services, CUSTOMERS, RunContext(run_id="run-failed"), ExecutionMode.FULL)

    manifest_path = tmp_path / "default" / "customers" / "run-failed" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert result.status == ExecutionStatus.FAILED
    assert manifest["status"] == "failed"
    assert "supabase unavailable" in manifest["error"]
    assert checkpoints.values == {}


def test_in_memory_sink_upsert_is_idempotent() -> None:
    sink = InMemorySupabaseSink()
    worker = LoadWorker(sink)
    worker.load(CUSTOMERS, [])
    worker.load(CUSTOMERS, [])
    assert sink.records == {}


def test_replay_reads_persisted_pages_without_extractor_network(tmp_path: Path) -> None:
    raw_store = LocalRawStore(tmp_path)
    context = RunContext(run_id="run-replay")
    raw_store.write_page(context, CUSTOMERS, customer_page())
    assert len(raw_store.read_pages(context, CUSTOMERS)) == 1

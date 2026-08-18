from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .models import ExecutionMode, ExecutionStatus, RawRunManifest, ResourceSpec, RunContext
from .ports import CheckpointStorePort, ExtractorPort, LoaderPort, RawStorePort, TransformerPort


@dataclass(slots=True)
class RunResult:
    manifest: RawRunManifest
    status: ExecutionStatus
    records_loaded: int = 0
    records_rejected: int = 0


@dataclass(slots=True)
class PipelineServices:
    extractor: ExtractorPort
    raw_store: RawStorePort
    transformer: TransformerPort
    loader: LoaderPort
    checkpoints: CheckpointStorePort | None = None


def execute_resource(
    services: PipelineServices,
    resource: ResourceSpec,
    context: RunContext,
    mode: ExecutionMode,
) -> RunResult:
    pages = []
    normalized = []
    rejected = []
    try:
        pages = list(services.extractor.extract(resource, context, mode))
        for page in pages:
            services.raw_store.write_page(context, resource, page)

        normalized, rejected = services.transformer.transform(resource, pages)
        services.raw_store.write_rejections(context, resource, rejected)
        services.loader.load(resource, normalized)

        status = ExecutionStatus.SUCCESS if not rejected else ExecutionStatus.PARTIAL
        manifest = RawRunManifest(
            run_id=context.run_id,
            resource=resource.name,
            account_id=context.account_id,
            mode=mode,
            started_at=context.started_at,
            finished_at=datetime.now(timezone.utc),
            page_count=len(pages),
            record_count=len(normalized) + len(rejected),
            status=status,
        )
        services.raw_store.write_manifest(context, manifest)

        if services.checkpoints and normalized and status == ExecutionStatus.SUCCESS:
            services.checkpoints.set(resource.name.value, normalized[-1].external_id)

        return RunResult(
            manifest=manifest,
            status=manifest.status,
            records_loaded=len(normalized),
            records_rejected=len(rejected),
        )
    except Exception as exc:
        manifest = RawRunManifest(
            run_id=context.run_id,
            resource=resource.name,
            account_id=context.account_id,
            mode=mode,
            started_at=context.started_at,
            finished_at=datetime.now(timezone.utc),
            page_count=len(pages),
            record_count=len(normalized) + len(rejected),
            status=ExecutionStatus.FAILED,
            error=f"{type(exc).__name__}: {exc}",
        )
        services.raw_store.write_manifest(context, manifest)
        return RunResult(
            manifest=manifest,
            status=manifest.status,
            records_loaded=len(normalized),
            records_rejected=len(rejected),
        )

from __future__ import annotations

import argparse

from config import AppConfig
from core.catalog import InMemoryResourceCatalog
from core.models import ExecutionMode, RawRunManifest, ExecutionStatus, RunContext
from core.use_cases import PipelineServices
from extract.omie_client import OmieClient, OmieCredentials
from extract.raw_store import LocalRawStore
from extract.resources import CUSTOMERS, SERVICES
from extract.worker import ExtractWorker
from extract.rate_limit import RetryPolicy
from load.local_sink import InMemorySupabaseSink
from load.supabase_sink import SupabaseRestSink
from load.worker import LoadWorker
from pipeline.replay import ReplayRunner
from pipeline.runner import PipelineRunner
from transform.workers import transform_resource


class ResourceTransformer:
    def transform(self, resource, pages):
        return transform_resource(resource, list(pages))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline local Omie -> raw -> transform -> load")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("run", "extract"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--resource", choices=("customers", "services", "all"), default="all")
        subparser.add_argument("--mode", choices=("full", "incremental"), default="full")

    replay = subparsers.add_parser("replay")
    replay.add_argument("--resource", choices=("customers", "services"), required=True)
    replay.add_argument("--run-id", required=True)
    return parser


def _resources(name: str):
    catalog = InMemoryResourceCatalog((CUSTOMERS, SERVICES))
    return catalog, list(catalog.list()) if name == "all" else [catalog.get(name)]


def _services(config: AppConfig, *, use_supabase: bool) -> tuple[PipelineServices, LocalRawStore]:
    raw_store = LocalRawStore(config.raw_data_dir)
    client = OmieClient(
        OmieCredentials(config.omie_app_key, config.omie_app_secret),
        timeout_seconds=config.http_timeout,
        retry_policy=RetryPolicy(max_retries=config.http_max_retries),
    )
    services = PipelineServices(
        extractor=ExtractWorker(client),
        raw_store=raw_store,
        transformer=ResourceTransformer(),
        loader=LoadWorker(
            SupabaseRestSink(config.supabase_url, config.supabase_service_role_key, config.load_batch_size)
            if use_supabase
            else InMemorySupabaseSink()
        ),
    )
    return services, raw_store


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AppConfig.from_env()
    catalog, selected = _resources(getattr(args, "resource", "all"))
    if args.command in {"run", "extract"}:
        config.validate_extract_config()
    if args.command in {"run", "replay"}:
        config.validate_load_config()
    services, raw_store = _services(config, use_supabase=args.command in {"run", "replay"})

    if args.command == "replay":
        result = ReplayRunner(services, raw_store).run(selected[0], args.run_id, config.omie_company_id)
        print(result.status.value)
        return 0 if result.status != ExecutionStatus.FAILED else 1

    mode = ExecutionMode(getattr(args, "mode", "full"))
    if args.command == "extract":
        for resource in selected:
            context = RunContext(account_id=config.omie_company_id)
            pages = list(services.extractor.extract(resource, context, mode))
            for page in pages:
                services.raw_store.write_page(context, resource, page)
            services.raw_store.write_manifest(
                context,
                RawRunManifest(
                    run_id=context.run_id,
                    resource=resource.name,
                    account_id=context.account_id,
                    mode=mode,
                    started_at=context.started_at,
                    page_count=len(pages),
                    status=ExecutionStatus.SUCCESS,
                ),
            )
            print(f"{resource.name.value}: {context.run_id}")
        return 0

    runner = PipelineRunner(catalog, services)
    results = runner.run_all(mode, config.omie_company_id) if args.resource == "all" else [
        runner.run(args.resource, mode, config.omie_company_id)
    ]
    for result in results:
        print(f"{result.manifest.resource.value}: {result.status.value}")
    return 0 if all(result.status != ExecutionStatus.FAILED for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

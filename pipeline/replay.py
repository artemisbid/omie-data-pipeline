from __future__ import annotations

from dataclasses import dataclass

from core.models import ExecutionMode, ResourceSpec, RunContext
from core.use_cases import PipelineServices, RunResult, execute_resource
from extract.replay import ReplayExtractor
from extract.raw_store import LocalRawStore


@dataclass(slots=True)
class ReplayRunner:
    services: PipelineServices
    raw_store: LocalRawStore

    def run(self, resource: ResourceSpec, run_id: str, account_id: str | None = None) -> RunResult:
        context = RunContext(run_id=run_id, account_id=account_id)
        replay_services = PipelineServices(
            extractor=ReplayExtractor(self.raw_store),
            raw_store=self.raw_store,
            transformer=self.services.transformer,
            loader=self.services.loader,
            checkpoints=self.services.checkpoints,
        )
        return execute_resource(replay_services, resource, context, ExecutionMode.REPLAY)

from __future__ import annotations

from dataclasses import dataclass

from core.models import ExecutionMode, RunContext
from core.ports import ResourceCatalog
from core.use_cases import PipelineServices, RunResult, execute_resource


@dataclass(slots=True)
class PipelineRunner:
    catalog: ResourceCatalog
    services: PipelineServices

    def run(self, resource_name: str, mode: ExecutionMode, account_id: str | None = None) -> RunResult:
        resource = self.catalog.get(resource_name)
        return execute_resource(self.services, resource, RunContext(account_id=account_id), mode)

    def run_all(self, mode: ExecutionMode, account_id: str | None = None) -> list[RunResult]:
        results: list[RunResult] = []
        for resource in self.catalog.list():
            results.append(self.run(resource.name.value, mode, account_id=account_id))
        return results

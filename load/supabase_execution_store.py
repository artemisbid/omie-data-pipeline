from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from urllib import error, parse, request

from core.exceptions import LoadError
from core.models import RawRunManifest, RejectedRecord, ResourceSpec, RunContext
from core.ports import CheckpointStorePort, ExecutionStorePort


@dataclass(slots=True)
class SupabaseExecutionStore(ExecutionStorePort, CheckpointStorePort):
    url: str
    service_role_key: str
    timeout_seconds: int = 30

    def start(self, manifest: RawRunManifest) -> None:
        self._upsert("pipeline_runs", [self._manifest_row(manifest)], "run_id")

    def finish(self, manifest: RawRunManifest) -> None:
        self._upsert("pipeline_runs", [self._manifest_row(manifest)], "run_id")

    def write_rejections(
        self,
        context: RunContext,
        resource: ResourceSpec,
        rejected: Sequence[RejectedRecord],
    ) -> None:
        if not rejected:
            return
        rows = [
            {
                "run_id": context.run_id,
                "resource": resource.name.value,
                "reason": item.reason,
                "source_payload": dict(item.source_payload),
            }
            for item in rejected
        ]
        self._post("pipeline_rejections", rows)

    def get(self, resource_name: str) -> str | None:
        query = parse.urlencode({"resource": f"eq.{resource_name}", "select": "checkpoint"})
        rows = self._request("pipeline_checkpoints", method="GET", query=query)
        return rows[0].get("checkpoint") if rows else None

    def set(self, resource_name: str, checkpoint: str) -> None:
        self._upsert(
            "pipeline_checkpoints",
            [{"resource": resource_name, "checkpoint": checkpoint}],
            "resource",
        )

    @staticmethod
    def _manifest_row(manifest: RawRunManifest) -> dict:
        return {
            "run_id": manifest.run_id,
            "resource": manifest.resource.value,
            "account_id": manifest.account_id,
            "mode": manifest.mode.value,
            "status": manifest.status.value,
            "started_at": manifest.started_at.isoformat(),
            "finished_at": manifest.finished_at.isoformat() if manifest.finished_at else None,
            "page_count": manifest.page_count,
            "record_count": manifest.record_count,
            "error": manifest.error,
        }

    def _upsert(self, table: str, rows: list[dict], conflict_column: str) -> None:
        self._post(table, rows, query=parse.urlencode({"on_conflict": conflict_column}), prefer="resolution=merge-duplicates,return=minimal")

    def _post(self, table: str, rows: list[dict], *, query: str = "", prefer: str = "return=minimal") -> None:
        self._request(table, method="POST", query=query, body=rows, prefer=prefer)

    def _request(
        self,
        table: str,
        *,
        method: str,
        query: str = "",
        body: list[dict] | None = None,
        prefer: str = "return=minimal",
    ) -> list[dict]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        if query:
            endpoint = f"{endpoint}?{query}"
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        req = request.Request(
            endpoint,
            data=encoded,
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
                "Prefer": prefer,
            },
            method=method,
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else []
        except error.HTTPError as exc:
            raise LoadError(f"Supabase operational write failed with HTTP {exc.code}") from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LoadError("Supabase operational write failed") from exc

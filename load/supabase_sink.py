from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from urllib import error, request

from core.exceptions import LoadError
from core.models import NormalizedRecord, ResourceSpec

from .port import SupabaseWriterPort


@dataclass(slots=True)
class SupabaseRestSink(SupabaseWriterPort):
    url: str
    service_role_key: str
    batch_size: int = 500
    timeout_seconds: int = 30

    def upsert(self, resource: ResourceSpec, records: Sequence[NormalizedRecord]) -> None:
        if self.batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")
        table = str(resource.metadata.get("target_table", resource.name.value))
        conflict_column = str(resource.metadata.get("conflict_column", "external_id"))
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"

        for start in range(0, len(records), self.batch_size):
            batch = records[start : start + self.batch_size]
            payload = [self._row(record) for record in batch]
            self._post(endpoint, payload, conflict_column)

    @staticmethod
    def _row(record: NormalizedRecord) -> dict:
        return {"external_id": record.external_id, **dict(record.data), "source_payload": dict(record.source_payload)}

    def _post(self, endpoint: str, payload: list[dict], conflict_column: str) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            f"{endpoint}?on_conflict={conflict_column}",
            data=body,
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds):
                return
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")[:500]
            raise LoadError(f"Supabase upsert failed with HTTP {exc.code}: {details}") from exc
        except (error.URLError, TimeoutError) as exc:
            raise LoadError(f"Supabase upsert failed due to network error: {exc}") from exc

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from collections.abc import Sequence

from core.models import RawPage, RawRunManifest, RejectedRecord, ResourceSpec, RunContext
from core.ports import RawStorePort


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


@dataclass(slots=True)
class LocalRawStore(RawStorePort):
    base_dir: Path

    def write_page(self, context: RunContext, resource: ResourceSpec, page: RawPage) -> None:
        pages_dir = self._pages_dir(context, resource)
        pages_dir.mkdir(parents=True, exist_ok=True)
        target = pages_dir / f"page_{page.page_number:04d}.json"
        self._atomic_write(target, json.dumps(page.payload, ensure_ascii=False, indent=2, default=_json_default))

    def write_manifest(self, context: RunContext, manifest: RawRunManifest) -> None:
        base_path = self._run_dir(context, manifest.resource.value)
        base_path.mkdir(parents=True, exist_ok=True)
        target = base_path / "manifest.json"
        self._atomic_write(target, json.dumps(asdict(manifest), ensure_ascii=False, indent=2, default=_json_default))

    def write_rejections(
        self,
        context: RunContext,
        resource: ResourceSpec,
        rejected: list[RejectedRecord] | tuple[RejectedRecord, ...],
    ) -> None:
        target = self._run_dir(context, resource.name.value) / "rejected.json"
        payload = [asdict(item) for item in rejected]
        self._atomic_write(target, json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default))

    def read_pages(self, context: RunContext, resource: ResourceSpec) -> Sequence[RawPage]:
        pages_dir = self._pages_dir(context, resource)
        pages: list[RawPage] = []
        for path in sorted(pages_dir.glob("page_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            page_number = int(path.stem.removeprefix("page_"))
            pages.append(RawPage(page_number=page_number, payload=payload))
        return pages

    def _pages_dir(self, context: RunContext, resource: ResourceSpec) -> Path:
        return self._run_dir(context, resource.name.value) / "pages"

    def _run_dir(self, context: RunContext, resource_name: str) -> Path:
        account = context.account_id or "default"
        return self.base_dir / account / resource_name / context.run_id

    @staticmethod
    def _atomic_write(target: Path, content: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)

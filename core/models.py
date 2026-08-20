from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping
from uuid import uuid4


class ResourceName(StrEnum):
    CUSTOMERS = "customers"
    SERVICES = "services"
    RECEIVABLES = "receivables"
    CATEGORIES = "categories"


class ExecutionMode(StrEnum):
    FULL = "full"
    INCREMENTAL = "incremental"
    REPLAY = "replay"


class ExecutionStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str = field(default_factory=lambda: uuid4().hex)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    account_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResourceSpec:
    name: ResourceName
    endpoint: str
    method: str
    stable_key: str
    supports_incremental: bool = False
    default_mode: ExecutionMode = ExecutionMode.INCREMENTAL
    page_size: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RawPage:
    page_number: int
    payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class RawRunManifest:
    run_id: str
    resource: ResourceName
    account_id: str | None
    mode: ExecutionMode
    started_at: datetime
    finished_at: datetime | None = None
    page_count: int = 0
    record_count: int = 0
    status: ExecutionStatus = ExecutionStatus.RUNNING
    error: str | None = None


@dataclass(frozen=True, slots=True)
class NormalizedRecord:
    source: ResourceName
    external_id: str
    data: Mapping[str, Any]
    source_payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class RejectedRecord:
    source: ResourceName
    source_payload: Mapping[str, Any]
    reason: str

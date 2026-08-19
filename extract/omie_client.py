from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any
from urllib import error, request

from core.models import RawPage, ResourceSpec
from core.exceptions import ExtractError

from .pagination import build_page_params, has_more_pages
from .rate_limit import RetryPolicy


@dataclass(slots=True)
class OmieCredentials:
    app_key: str
    app_secret: str


@dataclass(slots=True)
class OmieClient:
    credentials: OmieCredentials
    timeout_seconds: int = 30
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    def post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        last_error: Exception | None = None
        for attempt in range(1, self.retry_policy.max_retries + 1):
            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                last_error = exc
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or not self.retry_policy.should_retry(attempt):
                    break
                self.retry_policy.wait(attempt)
            except (error.URLError, TimeoutError) as exc:
                last_error = exc
                if not self.retry_policy.should_retry(attempt):
                    break
                self.retry_policy.wait(attempt)
            except json.JSONDecodeError as exc:
                raise ExtractError(f"Omie returned invalid JSON for endpoint={endpoint}") from exc

        raise ExtractError(f"Omie request failed for endpoint={endpoint}") from last_error

    def list_pages(
        self,
        resource: ResourceSpec,
        *,
        page_size: int,
        extra_params: dict[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> list[RawPage]:
        if max_pages is not None and max_pages <= 0:
            raise ValueError("max_pages must be greater than zero when provided")
        payload_key = str(resource.metadata.get("payload_key", "cadastros"))
        page_param = str(resource.metadata.get("page_param", "pagina"))
        page_size_param = str(resource.metadata.get("page_size_param", "registros_por_pagina"))
        total_pages_key = str(resource.metadata.get("total_pages_key", "total_de_paginas"))
        current_page = 1
        pages: list[RawPage] = []

        while True:
            params = build_page_params(
                current_page,
                page_size,
                extra_params,
                page_param=page_param,
                page_size_param=page_size_param,
            )
            response = self.post(
                resource.endpoint,
                {
                    "call": resource.method,
                    "app_key": self.credentials.app_key,
                    "app_secret": self.credentials.app_secret,
                    "param": [params],
                },
            )
            pages.append(RawPage(page_number=current_page, payload=response))

            if max_pages is not None and len(pages) >= max_pages:
                break

            if not has_more_pages(response, current_page, payload_key, total_pages_key=total_pages_key):
                break

            current_page += 1

        return pages

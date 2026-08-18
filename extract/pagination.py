from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def chunk_items(items: list[dict], page_size: int) -> Iterable[list[dict]]:
    if page_size <= 0:
        raise ValueError("page_size must be greater than zero")

    for index in range(0, len(items), page_size):
        yield items[index : index + page_size]


def build_page_params(page_number: int, page_size: int, extra_params: Mapping[str, Any] | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {
        "pagina": page_number,
        "registros_por_pagina": page_size,
    }
    if extra_params:
        params.update(extra_params)
    return params


def get_total_pages(payload: Mapping[str, Any]) -> int | None:
    raw_value = payload.get("total_de_paginas")
    if raw_value is None:
        return None

    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None


def has_more_pages(payload: Mapping[str, Any], current_page: int, payload_key: str) -> bool:
    total_pages = get_total_pages(payload)
    if total_pages is not None:
        return current_page < total_pages

    items = payload.get(payload_key, [])
    return bool(items)

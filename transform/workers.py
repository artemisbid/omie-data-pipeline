from __future__ import annotations

from core.models import RawPage, RejectedRecord, ResourceName, ResourceSpec

from .customers import transform_customers
from .services import transform_services


def transform_resource(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list, list[RejectedRecord]]:
    if resource.name == ResourceName.CUSTOMERS:
        return transform_customers(resource, pages)
    if resource.name == ResourceName.SERVICES:
        return transform_services(resource, pages)
    raise ValueError(f"Unsupported resource: {resource.name}")

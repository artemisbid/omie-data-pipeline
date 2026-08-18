from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import ResourceSpec


@dataclass(slots=True)
class InMemoryResourceCatalog:
    resources: Sequence[ResourceSpec]

    def list(self) -> Sequence[ResourceSpec]:
        return self.resources

    def get(self, name: str) -> ResourceSpec:
        for resource in self.resources:
            if resource.name.value == name:
                return resource
        raise KeyError(name)


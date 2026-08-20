from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Allocation:
    code: str | None
    name: str | None
    percentage: Decimal
    amount: Decimal


def _decimal(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value).replace(",", "."))


def allocate_amount(original_amount: Any, entries: list[dict[str, Any]] | None) -> list[Allocation]:
    """Distribute an amount while preserving the original total to cents.

    Entries may provide a percentage (``nPerDep``/``percentual``) and an
    explicit amount (``nValDep``/``valor``). Explicit amounts are preferred;
    otherwise the amount is calculated from the percentage. An empty rateio
    means 100% allocated to an unclassified bucket.
    """
    original = _decimal(original_amount).quantize(CENT, rounding=ROUND_HALF_UP)
    if not entries:
        return [Allocation(None, None, Decimal("100"), original)]

    allocations: list[Allocation] = []
    for entry in entries:
        percentage = _decimal(entry.get("nPerDep", entry.get("percentual", 0)))
        explicit = entry.get("nValDep", entry.get("valor"))
        amount = _decimal(explicit) if explicit not in (None, "") else original * percentage / Decimal("100")
        allocations.append(Allocation(
            code=str(entry.get("cCodDep", entry.get("codigo_categoria", ""))) or None,
            name=str(entry.get("cDesDep", "")) or None,
            percentage=percentage,
            amount=amount.quantize(CENT, rounding=ROUND_HALF_UP),
        ))

    residual = original - sum((item.amount for item in allocations), Decimal("0"))
    if residual:
        last = allocations[-1]
        allocations[-1] = Allocation(last.code, last.name, last.percentage, last.amount + residual)
    return allocations

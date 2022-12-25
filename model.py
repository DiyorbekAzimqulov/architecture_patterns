from dataclasses import dataclass
from typing import Optional, Set
from datetime import date


@dataclass(frozen=True)
class Orderline:
    order_ref: str
    sku: str
    qty: str


class Batch:

    def __init__(self, reference: str, sku: str, quantity: int, eta: Optional[date]) -> None:
        self.reference = reference
        self.sku = sku
        self.purchased_quantity = quantity
        self._allocations: Set[Orderline] = set()
        self.eta = eta
    
    def __gt__(self, other):
        if not self.eta:
            return False
        if not other.eta:
            return False
        return self.eta > other.eta

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __hash__(self) -> int:
        return hash(self.reference)
    
    def allocate(self, line: Orderline) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def can_allocate(self, line: Orderline) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    @property
    def allocated_quantity(self) -> int:
        return sum([line.qty for line in self._allocations])

    @property
    def available_quantity(self) -> int:
        return self.purchased_quantity - self.allocated_quantity

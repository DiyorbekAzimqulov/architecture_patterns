from dataclasses import dataclass
from typing import Optional, Set
from datetime import date

@dataclass(frozen=True)
class Orderline:
    reference: str
    sku: str
    qty: int


class Batch:

    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]) -> None:
        self.reference = ref
        self.sku = sku
        self._purchased_qty = quantity
        self.eta = eta
        self._allocations: Set[Orderline] = set() # Set[Orderline]

    def __eq__(self, other) -> bool:
        if isinstance(other, Batch) is False:
            return False
        return self.reference == other.reference
    
    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return False
        return self.eta > other.eta

    def __hash__(self) -> int:
        return hash(self.reference)
    
    def allocate(self, line: Orderline) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: Orderline) -> None:
        if line in self._allocations:
            self._allocations.remove(line)
    
    def can_allocate(self, line: Orderline) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
    

    @property
    def allocated_quantity(self) -> int:
        return sum([line.qty for line in self._allocations])

    @property
    def available_quantity(self) -> int:
        return self._purchased_qty - self.allocated_quantity

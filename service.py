from typing import List

from model import Orderline, Batch
from exceptions import OutOfStock


def allocate(line: Orderline, batches: List[Batch]) -> str:
    try:
        batch = next(
            batch for batch in sorted(batches) if batch.can_allocate(line)
        )
    except StopIteration:
        raise OutOfStock(f'Can not allocate for line {line.sku}')
    
    batch.allocate(line)
    return batch.reference

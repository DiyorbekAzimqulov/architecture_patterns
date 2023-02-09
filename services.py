from __future__ import annotations

import model
from model import OrderLine, Batch
from repository import AbstractRepository


class InvalidSku(Exception):
    pass

class LineNotAllocated(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def add_batch(batch: Batch, repo: AbstractRepository, session) -> None:
    repo.add(batch)
    session.commit()


def deallocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    try:
        batch = next(b for b in sorted(repo.list()) if b.is_line_allocated(line))
        batch.deallocate(line)
    except StopIteration:
        raise LineNotAllocated(f'Line {line.sku} not allocated for any batches!')
    session.commit()
    return batch.reference

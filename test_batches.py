from datetime import date, timedelta

import pytest

from model import Batch, Orderline
from service import allocate
from exceptions import OutOfStock


today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)


def make_batch_n_line(sku: str, batch_qty: int, line_qty: int):
    batch = Batch('batch-001', sku, batch_qty, None)
    line = Orderline('order-001', sku, line_qty)
    return batch, line


def test_allocate_orderline_to_batch_reduces_available_quantity():
    batch, line = make_batch_n_line('TABLE', 100, 2)
    batch.allocate(line)

    assert batch.available_quantity == 98

def test_can_allocate_if_available_qty_gte_line_qty():
    batch, line = make_batch_n_line('TABLE', 100, 2)
    assert batch.can_allocate(line) == True


def test_can_allocate_if_available_qty_e_line_qty():
    batch, line = make_batch_n_line('TABLE', 100, 100)
    assert batch.can_allocate(line) == True


def test_can_not_allocate_if_available_qty_lt_line_qty():
    batch, line = make_batch_n_line('TABLE', 10, 100)
    assert batch.can_allocate(line) == False

def test_deallocate_only_allocated_lines_to_batch():
    batch, unallocated_line = make_batch_n_line('TABLE', 100, 10)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 100
    batch.allocate(unallocated_line)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 100

def test_allocation_unique():
    batch, unallocated_line = make_batch_n_line('TABLE', 100, 10)
    batch.allocate(unallocated_line)
    batch.allocate(unallocated_line)
    assert batch.available_quantity == 90


def test_prefers_in_stock_batch():
    batch1 = Batch('batch-001', 'TABLE', 10, eta=None)
    batch2 = Batch('batch-002', 'TABLE', 10, eta=later)
    line = Orderline('order-ref', 'TABLE', 2)
    allocate(line, [batch1, batch2])
    assert batch1.available_quantity == 8


def test_prefers_earliest_stock_batch():
    batch1 = Batch('batch-001', 'TABLE', 10, eta=today)
    batch2 = Batch('batch-002', 'TABLE', 10, eta=tomorrow)
    batch3 = Batch('batch-003', 'TABLE', 10, eta=later)
    line = Orderline('order-ref', 'TABLE', 2)
    allocate(line, [batch1, batch2, batch3])
    assert batch1.available_quantity == 8


def test_allocate_returns_batch_reference():
    batch1 = Batch('batch-001', 'TABLE', 10, eta=today)
    line = Orderline('order-ref', 'TABLE', 2)
    allocation = allocate(line, [batch1])
    assert batch1.reference == allocation

def test_raises_out_of_stock_exception():
    batch1 = Batch('batch-001', 'TABLE', 10, eta=today)
    line = Orderline('order-ref', 'TABLE', 12)

    with pytest.raises(OutOfStock):
        allocate(line, [batch1])

import pytest
from datetime import date, timedelta

from exceptions import OutOfStock
from model import Orderline, Batch
from service import allocate


today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(15)


def make_line_n_batch(sku, batch_qty, sku_qty):
    batch = Batch("batch-01", sku, batch_qty, None)
    line = Orderline("order-01", sku, sku_qty)
    return batch, line


def test_allocate_reduces_available_quantity():

    batch, line = make_line_n_batch("TABLE", 20, 2)
    batch.allocate(line)

    assert batch.available_quantity == 18

def test_can_not_allocate_if_sku_do_not_match():

    batch, line = make_line_n_batch("TABLE", 20, 2)
    other_line = Orderline('order-01', "CHAIR", 2)
    batch.allocate(other_line)

    assert batch.available_quantity == 20

def test_allocate_only_if_available_quantity_gte_line_qty():
    batch, line = make_line_n_batch("TABLE", 10, 20)
    batch.allocate(line)

    assert batch.available_quantity == 10


def test_can_not_allocate_one_line_twice():
    batch, line = make_line_n_batch("TABLE", 20, 2)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_prefer_warehouse_stock():
    in_stock = Batch("batch-01", "TABLE", 10, None)
    today_stock = Batch("batch-02", "TABLE", 10, today)
    tomorrow_stock = Batch("batch-03", "TABLE", 10, tomorrow)
    line = Orderline("order-01", "TABLE", 2)

    allocate(line, [in_stock, today_stock, tomorrow_stock])
    assert in_stock.available_quantity == 8
    assert today_stock.available_quantity == 10
    assert tomorrow_stock.available_quantity == 10
    

def test_prefer_earliest_batch():
    today_stock = Batch("batch-02", "TABLE", 10, today)
    tomorrow_stock = Batch("batch-03", "TABLE", 10, tomorrow)
    line = Orderline("order-01", "TABLE", 2)
    allocate(line, [today_stock, tomorrow_stock])
    assert today_stock.available_quantity == 8
    assert tomorrow_stock.available_quantity == 10

def test_allocate_returns_allocated_batch_reference():
    in_stock = Batch("batch-01", "TABLE", 10, None)
    today_stock = Batch("batch-02", "TABLE", 10, today)
    line = Orderline("order-01", "TABLE", 2)
    
    reference = allocate(line, [in_stock, today_stock])

    assert in_stock.reference == reference

def test_returns_out_of_stock_exception_if_not_available_batch():
    in_stock = Batch("batch-01", "TABLE", 10, None)
    today_stock = Batch("batch-02", "TABLE", 10, today)
    line = Orderline("order-01", "TABLE", 20)
    
    with pytest.raises(OutOfStock):
        allocate(line, [in_stock, today_stock])

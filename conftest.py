import sqlite3
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, start_mappers


@pytest.fixture
def sqlite_session():
    order_lines = """CREATE TABLE IF NOT EXISTS order_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku VARCHAR(255),
                    qty INTEGER NOT NULL,
                    orderid VARCHAR(255)
                );
                """

    batches = """CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference VARCHAR(255),
                sku VARCHAR(255),
                _purchased_quantity INTEGER NOT NULL,
                eta DATE
                );
                """

    allocations = """CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orderline_id INTEGER,
                batch_id INTEGER,
                FOREIGN KEY (orderline_id) REFERENCES order_lines (id),
                FOREIGN KEY (batch_id) REFERENCES batches (id)
                );
                """
    connection = sqlite3.connect(':memory:')
    connection.execute(order_lines)
    connection.execute(batches)
    connection.execute(allocations)
    yield connection
    connection.close()


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()

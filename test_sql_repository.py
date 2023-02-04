import model
import repository


def test_sql_repository_can_save_a_batch(sqlite_session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlRepository(sqlite_session)
    repo.add(batch)
    sqlite_session.commit()
    rows = sqlite_session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]

def test_sql_repository_can_retrieve_a_batch(sqlite_session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlRepository(sqlite_session)
    repo.add(batch)
    sqlite_session.commit()
    result = repo.get('batch1')
    assert result == (1, "batch1", "RUSTY-SOAPDISH", 100, None)

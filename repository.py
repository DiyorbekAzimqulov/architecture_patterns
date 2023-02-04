import abc
import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class SqlRepository(AbstractRepository):

    def __init__(self, session) -> None:
        self.session = session

    def add(self, batch: model.Batch):
        insert_query = "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES (?, ?, ?, ?);"
        self.session.execute(insert_query, (batch.reference, batch.sku, batch._purchased_quantity, batch.eta))

    def get(self, reference):
        retrieve_query = "SELECT * from batches WHERE reference=?;"
        return self.session.execute(retrieve_query, (reference,)).fetchone()

    def list(self):
        return self.session.execute("SELECT * FROM batches;")

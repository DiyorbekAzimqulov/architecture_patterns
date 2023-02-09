from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import repository
import services


orm.start_mappers()
engine = create_engine(config.get_postgres_uri())
# orm.metadata.create_all(engine)
get_session = sessionmaker(bind=engine)
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


@app.route("/batch", methods=["POST"])
def purchase_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    batch = model.Batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta=None
    )
    try:
        services.add_batch(batch, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400
    return {"batchref": batch.reference}, 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"],
    )
    try:
        batchref = services.deallocate(line, repo, session)
    except (services.LineNotAllocated) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201

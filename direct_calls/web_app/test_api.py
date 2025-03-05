import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from db.orm import get_db
from web_app.main import app

client = TestClient(app)

@pytest.fixture
def add_stock():
    session = next(get_db())
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            session.execute(
                text("INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES (:ref, :sku, :qty, :eta)"),
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = session.execute(
                text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        session.commit()

    yield _add_stock

    session = next(get_db())

    for batch_id in batches_added:
        session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"), dict(batch_id=batch_id),
        )
    for sku in skus_added:
        session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"), dict(sku=sku),
        )
        session.commit()


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku('other')
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock([
        (laterbatch, sku, 100, '2011-01-02'),
        (earlybatch, sku, 100, '2011-01-01'),
        (otherbatch, othersku, 100, None),
    ])
    data = {'order_id': random_orderid(), 'sku': sku, 'qty': 3}
    response = client.post("/allocate", json=data)
    assert response.status_code == 200
    assert response.json()['batchref'] == earlybatch


def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = { 'order_id': orderid, 'sku': unknown_sku, 'qty': 20 }
    response = client.post("/allocate", json=data)
    assert response.status_code == 400
    assert response.json()['detail'] == f'Invalid sku {unknown_sku}'

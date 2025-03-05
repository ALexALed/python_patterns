import pytest

from core.batches import OrderLine, Batch
from core.repository import AbstractRepository
from services.services import allocate, add_batch, InvalidSku


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True

class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

def test_returns_allocation():
    line = OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = allocate(line, repo, FakeSession())

def test_commits():
    line = OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    allocate(line, repo, session)
    assert session.committed is True

def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"

def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("b1", "AREALSKU", 100, None, repo, session)
    with pytest.raises(InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())
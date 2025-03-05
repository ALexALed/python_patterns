import services.services
from services.test_services import FakeRepository


class FakeUnitOfWork:
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

def test_add_batch():
    uow = FakeUnitOfWork()
    services.services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.committed is True

def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "b1"

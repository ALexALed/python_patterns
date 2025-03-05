import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import repository
from core.product import Product
from db.orm import DB_URL

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(DB_URL))

class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class AbstractProductRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, product):
        ...

    @abc.abstractmethod
    def get(self, sku) -> Product:
        ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
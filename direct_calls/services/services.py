import typing
from datetime import date

from core import allocate as allocate_core
from core.batches import OrderLine, Batch
from core.product import Product
from core.repository import AbstractRepository
from services import message_bus
from services.unit_of_work import AbstractUnitOfWork


class CanCommit(typing.Protocol):
    def commit(self):
        ...


class InvalidSku(Exception):
    pass

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(sku=line.sku)
        if not product:
            raise InvalidSku(f"Invalid sku {line.sku}")
        try:
            batchref = product.allocate(line)
            uow.commit()
            return batchref
        finally:
            message_bus.handle(product.events)


def add_batch(ref: str, sku: str, qty: int, eta: typing.Optional[date], uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(ref, sku, qty, eta))
        uow.commit()
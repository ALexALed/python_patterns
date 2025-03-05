from typing import List

from core.allocate import OutOfStock
from core.batches import Batch, OrderLine
from core.events import Event, OutOfStock as OutOfStockEvent


class Product:

    def __init__(self, sku: str, batches: List[Batch]):
        self.sku = sku
        self.batches = batches
        self.events: list[Event] = []

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(
                b for b in sorted(self.batches) if b.can_allocate(line)
            )
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            self.events.append(OutOfStockEvent(line.sku))
            raise OutOfStock(f'Out of stock for sku {line.sku}')

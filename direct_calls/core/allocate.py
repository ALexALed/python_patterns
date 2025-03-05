from core.batches import Batch, OrderLine

class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]):
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(
            f"Out of stock for sku {line.sku} in any of the batches"
        )
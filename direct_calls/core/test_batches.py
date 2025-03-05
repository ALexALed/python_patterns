from datetime import date

from core.batches import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "small-eel", qty=20, eta=date.today())
    line = OrderLine('order-ref', "small-eel", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18

def make_batch_and_line(sku, batch_qty, line_qty):
    return Batch("batch-001", sku, qty=batch_qty, eta=date.today()), OrderLine('order-ref', sku, line_qty)

def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line("small-eel", 20, 2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_batch_and_line("small-eel", 2, 20)
    assert not batch.can_allocate(line)

def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("small-eel", 2, 2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_sku_do_not_match():
    batch = Batch("batch-001", "small-trt", qty=20, eta=date.today())
    line = OrderLine('order-ref', "small-eel", 2)
    assert not batch.can_allocate(line)

def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("small-eel", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
from core.events import Event, OutOfStock

def handle(event: Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

def send_out_of_stock_notification(event: OutOfStock):
    pass
    # email.send_email("e@e.com", f"Out of stock for {event.sku}")



HANDLERS = {
    OutOfStock: [send_out_of_stock_notification]
}
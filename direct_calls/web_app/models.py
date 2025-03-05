from pydantic import BaseModel


class AllocateRequest(BaseModel):
    order_id: str
    sku: str
    qty: int
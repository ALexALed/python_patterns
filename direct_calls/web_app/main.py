
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from services import services
from core.allocate import OutOfStock
from core.batches import OrderLine
from core.repository import SqlAlchemyRepository
from db.orm import get_db
from services.services import InvalidSku
from web_app.models import AllocateRequest

app = FastAPI()

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

@app.post("/allocate")
def allocate_lines(allocate_body: AllocateRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyRepository(db)
    line = OrderLine(
        allocate_body.order_id, allocate_body.sku, allocate_body.qty
    )

    try:
        batchref = services.allocate(line, repo, db)
    except (OutOfStock, InvalidSku) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"batchref": batchref}

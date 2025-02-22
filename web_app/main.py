from fastapi import FastAPI

from core.repository import SqlAlchemyRepository

app = FastAPI()

@app.post("/allocate")
def allocate():
    batches = SqlAlchemyRepository.list()
    
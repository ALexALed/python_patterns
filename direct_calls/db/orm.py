from dataclasses import dataclass, field

from sqlalchemy import Table, Column, MetaData, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import registry, relationship, sessionmaker

from core.batches import Batch, OrderLine

DB_URL = "sqlite:///./test.db"

engine = create_engine(DB_URL)

mapper_registry = registry()

order_lines = Table(
    'order_lines', mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer,nullable=False),
    Column('order_id', String(255))
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper, secondary=allocations, collection_class=set,
            )
        },
    )

mapper_registry.metadata.create_all(engine)
start_mappers()

def get_db():
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = db()
    try:
        yield session
    finally:
        session.close()
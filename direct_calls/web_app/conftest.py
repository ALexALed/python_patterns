import os

import pytest

from db import orm

@pytest.fixture(autouse=True)
def create_db():
    orm.DB_URL = "sqlite:///./test_test.db"
    yield



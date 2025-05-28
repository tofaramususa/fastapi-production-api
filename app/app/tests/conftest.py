import asyncio
from typing import Dict, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.core import AgnosticDatabase

from app.core.config import settings
from app.database.init_database import init_db
from app.main import app
from app.database.session import MongoDatabase, _MongoClientSingleton


@pytest_asyncio.fixture(scope="session")
async def db() -> Generator:
    db = MongoDatabase()
    _MongoClientSingleton.instance.mongo_client.get_io_loop = asyncio.get_event_loop
    await init_db(db)
    yield db


@pytest.fixture(scope="session")
def client(db) -> Generator:
    with TestClient(app=app, base_url="http://127.0.0.1:8000") as test_client:
        yield test_client


@pytest.fixture(scope="module")
def superuser_token_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {settings.MASTER_TOKEN}"}


@pytest.fixture(scope="module")
def unauthorized_headers() -> Dict[str, str]:
    """Fixture for testing unauthorized access"""
    return {"Authorization": "Bearer invalid_token"}


@pytest.fixture(scope="module")
def no_auth_headers() -> Dict[str, str]:
    """Fixture for testing requests without authentication"""
    return {}

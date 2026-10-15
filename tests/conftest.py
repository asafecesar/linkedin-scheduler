import os
import tempfile
import pytest
import pytest_asyncio
from pathlib import Path
import httpx

# Set temporary DATA_DIR before importing app modules
temp_dir = tempfile.TemporaryDirectory()
os.environ["DATA_DIR"] = temp_dir.name

from app import database as db
from app.main import app

@pytest.fixture(autouse=True)
def setup_test_db():
    db.init_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts")
    cursor.execute("DELETE FROM settings")
    conn.commit()
    conn.close()
    yield

@pytest_asyncio.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

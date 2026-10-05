import asyncio
import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.actions import classify_and_moderate
from db.models import Base, ModelVersion, Server
from db.session import SessionLocal, engine, init_db
from inference_service.app import app
from inference_service.model_loader import model_manager

# Create Test Client for FastAPI
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_database():
    """Setup clean in-memory / file SQLite tables before each test."""
    init_db()
    db = SessionLocal()
    # Ensure default model version exists
    db.query(ModelVersion).delete()
    default_v = ModelVersion(
        version_tag="v1.0.0-initial",
        trained_at=datetime.datetime.utcnow(),
        training_set_size=5000,
        f1_score=0.89,
        is_current=True,
    )
    db.add(default_v)
    db.commit()
    model_manager.load_model_from_db(db)
    yield db
    db.close()


def test_inference_health_check():
    """Test 1: Check endpoint /health returns 200, correct JSON schema, and model version."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "current_model_version_id" in data
    assert "version_tag" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_tc07_inference_timeout_handling(monkeypatch):
    """
    Test 2 (TC07): Mock request to inference service delayed by 2.5s (> 2.0s SLA).
    Assert bot catches timeout gracefully without unhandled exception, logs timeout, and bypasses message.
    """
    db = SessionLocal()
    server_cfg = Server(guild_id="test_guild", threshold_low=0.30, threshold_high=0.90)

    class MockMessage:
        id = 999111
        content = "Tin nhắn thử nghiệm timeout 2.5 giây"
        author = type("User", (), {"send": None, "__str__": lambda s: "TestUser"})()

    # Mock aiohttp session post method that sleeps for 2.5s
    class SlowResponseContextManager:
        async def __aenter__(self):
            await asyncio.sleep(2.5)  # Triggers > 2.0s timeout
            raise asyncio.TimeoutError("Simulated 2.5s network delay timeout")

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class DummyClientSession:
        def __init__(self, *args, **kwargs):
            pass

        def post(self, url, json=None, timeout=None):
            return SlowResponseContextManager()

        async def close(self):
            pass

    result = await classify_and_moderate(
        message=MockMessage(),
        server_config=server_cfg,
        db_session=db,
        session=DummyClientSession(),
    )

    # Verification: TC07 requirement -> Bypass message when timeout happens, no exception
    assert result["action"] == "bypass"
    assert result["reason"] == "timeout"
    db.close()


def test_model_hot_rollback():
    """
    Test 3: Model Hot-Rollback & Dynamic Switch
    1. Insert Version 1 (v1.0.0-old) and Version 2 (v2.0.0-new) into DB.
    2. Set Version 1 as is_current = True.
    3. Call endpoint /ops/reload.
    4. Confirm /health returns Version 1 without restarting the application.
    """
    db = SessionLocal()
    db.query(ModelVersion).delete()

    v1 = ModelVersion(
        version_tag="v1.0.0-old-stable",
        trained_at=datetime.datetime.utcnow(),
        training_set_size=10000,
        f1_score=0.88,
        is_current=False,
    )
    v2 = ModelVersion(
        version_tag="v2.0.0-new-buggy",
        trained_at=datetime.datetime.utcnow(),
        training_set_size=15000,
        f1_score=0.92,
        is_current=True,
    )
    db.add_all([v1, v2])
    db.commit()

    # Initial state -> v2.0.0-new-buggy
    model_manager.load_model_from_db(db)
    health1 = client.get("/health").json()
    assert health1["version_tag"] == "v2.0.0-new-buggy"

    # Step 2: Trigger Rollback in DB -> Set v1 as is_current=True, v2 as is_current=False
    v2.is_current = False
    v1.is_current = True
    db.commit()

    # Step 3: Trigger /ops/reload API endpoint
    reload_resp = client.post("/ops/reload")
    assert reload_resp.status_code == 200
    reload_data = reload_resp.json()
    assert reload_data["status"] == "success"
    assert reload_data["version_tag"] == "v1.0.0-old-stable"

    # Step 4: Verify /health returns rolled back Version 1
    health2 = client.get("/health").json()
    assert health2["version_tag"] == "v1.0.0-old-stable"
    assert health2["current_model_version_id"] == v1.model_version_id
    db.close()

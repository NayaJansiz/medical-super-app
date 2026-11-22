import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app import core, main


def test_health_returns_ok_when_database_is_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(core.database, "engine", test_engine)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    test_engine.dispose()


def test_health_returns_service_unavailable_without_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core.database, "engine", None)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 503

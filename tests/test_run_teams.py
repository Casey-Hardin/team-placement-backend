# native imports
from unittest.mock import Mock

# third-party imports
from fastapi.testclient import TestClient
import pytest

# external imports
from team_placement.api import app


client = TestClient(app)


@pytest.fixture
def my_fs(fs):
    """Use a fake and empty file system."""
    yield fs


@pytest.mark.usefixtures("my_fs")
def test_not_existant():
    """No objects exist."""
    response = client.post("/run-teams", json={})
    assert response.status_code == 422


@pytest.mark.usefixtures("my_fs")
def test_process(monkeypatch):
    """Objects are in the workspace."""
    run_mock = Mock()
    run_mock.return_value = []
    monkeypatch.setattr("team_placement.api.run_teams", run_mock)

    # run teams
    response = client.post(
        "/run-teams", json={"people": [], "controls": [], "teams": []}
    )

    assert response.status_code == 200
    run_mock.call_count == 1

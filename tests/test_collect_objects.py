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
    response_controls = client.get("/get-controls")
    response_nicknames = client.get("/get-nicknames")
    response_people = client.get("/get-people")
    response_teams = client.get("/get-teams")
    response_rooms = client.get("/get-rooms")
    responses = [
        response_controls,
        response_nicknames,
        response_people,
        response_teams,
        response_rooms,
    ]

    for response in responses:
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.usefixtures("my_fs")
def test_process(monkeypatch):
    """Objects are in the workspace."""
    collect_mock = Mock()
    collect_mock.return_value = []
    monkeypatch.setattr("team_placement.api.collect_objects", collect_mock)

    # collect objects
    response_controls = client.get("/get-controls")
    response_nicknames = client.get("/get-nicknames")
    response_people = client.get("/get-people")
    response_teams = client.get("/get-teams")
    response_rooms = client.get("/get-rooms")
    responses = [
        response_controls,
        response_nicknames,
        response_people,
        response_teams,
        response_rooms,
    ]

    for response in responses:
        assert response.status_code == 200
    collect_mock.call_count == 5

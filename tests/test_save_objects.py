# native imports
from unittest.mock import Mock

# third-party imports
from fastapi.testclient import TestClient
import pytest

# external imports
from team_placement.api import app
from team_placement.schemas import (
    BooleanEnum,
    Collective,
    Control,
    Gender,
    Nicknames,
    Person,
    Room,
    Team,
)

CONTROLS = [
    Control(
        index="Control",
        order=1,
        personIndex="Person",
        teamInclude=[""],
        teamExclude=[""],
        roomInclude=[""],
        roomExclude=[""],
    ),
]
NICKNAMES = [
    Nicknames(
        index="Test",
        firstName="Test",
        lastName="Doe",
        nicknames=["Champion", "Tester"],
    ),
]
PEOPLE = [
    Person(
        index="Person",
        order=1,
        firstName="John",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    )
]
ROOMS = [Room(index="Room", name="Room 1")]
TEAMS = [Team(index="Team", name="Team 1")]


client = TestClient(app)


@pytest.fixture
def my_fs(fs):
    yield fs


@pytest.mark.usefixtures("my_fs")
def test_empty_json():
    """Empty arguments are unprocessible."""
    response_controls = client.post("/save-controls", json={})
    response_nicknames = client.post("/save-nicknames", json={})
    response_people = client.post("/save-people", json={})
    response_teams = client.post("/save-teams", json={})
    response_rooms = client.post("/save-rooms", json={})
    responses = [
        response_controls,
        response_nicknames,
        response_people,
        response_teams,
        response_rooms,
    ]

    for response in responses:
        assert response.status_code == 422


@pytest.mark.usefixtures("my_fs")
def test_process(monkeypatch):
    """Save an analysis."""
    save_mock = Mock()
    save_mock.return_value = []
    monkeypatch.setattr("team_placement.api.save_objects", save_mock)

    # save objects
    response_controls = client.post(
        "/save-controls", json=[x.model_dump() for x in CONTROLS]
    )
    response_nicknames = client.post(
        "/save-nicknames", json=[x.model_dump() for x in NICKNAMES]
    )
    response_people = client.post("/save-people", json=[x.model_dump() for x in PEOPLE])
    response_teams = client.post("/save-teams", json=[x.model_dump() for x in TEAMS])
    response_rooms = client.post("/save-rooms", json=[x.model_dump() for x in ROOMS])
    responses = [
        response_controls,
        response_nicknames,
        response_people,
        response_teams,
        response_rooms,
    ]

    for response in responses:
        assert response.status_code == 200
    save_mock.call_count == 5

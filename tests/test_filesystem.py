# native imports
import json

# third-party imports
import pytest
from pydantic import BaseModel

# external imports
from team_placement.constants import (
    CONTROLS_FILE_PATH,
    NICKNAMES_FILE_PATH,
    PEOPLE_FILE_PATH,
    ROOMS_FILE_PATH,
    TEAMS_FILE_PATH,
)
from team_placement.filesystem import collect_objects, save_objects
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


INCORRECT_CONTROLS_FORMAT = {
    "index": "Controls",
    "order": 1,
    "personIndex": "Not a List",
    "teamInclude": [""],
    "teamExclude": [""],
    "roomInclude": [""],
    "roomExclude": [""],
}
INCORRECT_NICKNAMES_FORMAT = [
    {
        "index": "Nicknames",
        "firstName": "No Last Name",
        "nicknames": ["A", "Nickname"],
    }
]
INCORRECT_PEOPLE_FORMAT = [
    {
        "index": "Person",
        "firstName": "No Order",
        "lastName": "No Order",
        "age": 25,
        "gender": Gender.male,
        "firstTime": BooleanEnum.yes,
        "collective": Collective.new,
        "leader": BooleanEnum.no,
        "participant": BooleanEnum.yes,
    },
]
INCORRECT_ROOMS_FORMAT = [
    {"name": 5},
    {"name": "Name must be a string"},
]
INCORRECT_TEAMS_FORMAT = [
    {"name": "Team 1"},
    {"index": "Team", "name": "Index is missing"},
]


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


MODEL_TYPES: list[BaseModel] = [Control, Nicknames, Person, Room, Team]
PATHS = [
    CONTROLS_FILE_PATH,
    NICKNAMES_FILE_PATH,
    PEOPLE_FILE_PATH,
    ROOMS_FILE_PATH,
    TEAMS_FILE_PATH,
]
INCORRECT_FORMATS = [
    INCORRECT_CONTROLS_FORMAT,
    INCORRECT_NICKNAMES_FORMAT,
    INCORRECT_PEOPLE_FORMAT,
    INCORRECT_ROOMS_FORMAT,
    INCORRECT_TEAMS_FORMAT,
]
MODELS: list[list[BaseModel]] = [
    CONTROLS,
    NICKNAMES,
    PEOPLE,
    ROOMS,
    TEAMS,
]


@pytest.fixture
def my_fs(fs):
    yield fs


@pytest.mark.usefixtures("my_fs")
def test_collect_objects_no_objects():
    """Objects must return a list when files do not exist."""
    for model in MODEL_TYPES:
        assert collect_objects(model=model) == []


def test_collect_objects_incorrect_format(fs):
    """Objects must return a list when files are incorrect."""
    # create file paths
    for path in PATHS:
        fs.create_file(path)

    # write to files
    for path, incorrect_format in zip(PATHS, INCORRECT_FORMATS):
        with open(path, "w") as file_object:
            json.dump(incorrect_format, file_object, indent=2)

    # files must return empty
    for model in MODEL_TYPES:
        assert collect_objects(model=model) == []

    # incorrectly formatted files must be removed
    for path in PATHS:
        assert not path.exists()


def test_collect_objects(fs):
    """Objects must be collected from each object file."""
    # create file paths
    for path in PATHS:
        fs.create_file(path)

    # write to files
    for path, model in zip(PATHS, MODELS):
        with open(path, "w") as file_object:
            json.dump([object.model_dump() for object in model], file_object, indent=2)

    assert collect_objects(model=Control) == CONTROLS
    assert collect_objects(model=Nicknames) == NICKNAMES
    assert collect_objects(model=Person) == PEOPLE
    assert collect_objects(model=Room) == ROOMS
    assert collect_objects(model=Team) == TEAMS


@pytest.mark.usefixtures("my_fs")
def test_save_objects():
    """Objects must be saved to each object file."""
    for path, model_type, model in zip(PATHS, MODEL_TYPES, MODELS):
        save_objects(model=model_type, objects=model)

        with open(path, "r") as object_file:
            response = [model_type.model_validate(x) for x in json.load(object_file)]

        assert response == model

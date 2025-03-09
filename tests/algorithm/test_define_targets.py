# external imports
from team_placement.algorithm.define_targets import define_targets
from team_placement.schemas import (
    BooleanEnum,
    Collective,
    Gender,
    Person,
    Targets,
    Team,
)

TEAMS = [
    Team(index="Team 1", name="Team A"),
    Team(index="Team 2", name="Team B"),
]

PEOPLE = [
    Person(
        index="Person 1",
        order=1,
        firstName="Sally",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        team="Team 1",
    ),
    Person(
        index="Person 2",
        order=2,
        firstName="Lucy",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team 2",
    ),
    Person(
        index="Person 3",
        order=3,
        firstName="Tabitha",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.yes,
        collective=Collective.newish,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    ),
    Person(
        index="Person 4",
        order=4,
        firstName="Tracy",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.newish,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        team="Team 1",
    ),
    Person(
        index="Person 5",
        order=5,
        firstName="Drake",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.oldish,
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team 2",
    ),
    Person(
        index="Person 6",
        order=6,
        firstName="Josh",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.oldish,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    ),
]


def test_process():
    """Tests that targets are defined for team placement."""
    # define targets
    targets = define_targets(PEOPLE, TEAMS)
    assert targets == Targets(
        team_size=3,
        collective_new=1,
        collective_newish=1,
        collective_oldish=1,
        collective_old=0,
        age_std=0,
        girl_count=2,
    )

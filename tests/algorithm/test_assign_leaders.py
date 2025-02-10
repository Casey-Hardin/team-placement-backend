# external imports
from team_placement.algorithm.objects import PersonObject
from team_placement.algorithm.assign_leaders import assign_leaders
from team_placement.schemas import (
    BooleanEnum,
    Collective,
    Gender,
    Person,
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
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team A",
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
        team="Team B",
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
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team A",
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
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team B",
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
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    ),
]
PEOPLE = [PersonObject(x) for x in PEOPLE]

PEOPLE2 = [
    Person(
        index="Person 1",
        order=1,
        firstName="Sally",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.yes,
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
        team="Team 1",
    ),
    Person(
        index="Person 3",
        order=5,
        firstName="Drake",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.oldish,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    ),
]
PEOPLE2 = [PersonObject(x) for x in PEOPLE2]


def test_process():
    """Assigns leaders for team placement."""
    # define targets
    cohorts = assign_leaders(PEOPLE, TEAMS)
    assert len(cohorts) == 3
    assert len([x for x in cohorts if x.team == "Team A"]) == 1
    assert len([x for x in cohorts if x.team == "Team B"]) == 1
    assert len([x for x in cohorts if x.team == ""]) == 1

    cohorts = assign_leaders(PEOPLE2, TEAMS)
    assert len(cohorts) == 3
    print([x.team for x in cohorts])
    assert len([x for x in cohorts if x.team == "Team A"]) == 0
    assert len([x for x in cohorts if x.team == "Team B"]) == 0

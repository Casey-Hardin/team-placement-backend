# external imports
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
        cohort="Cohort 1",
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
        cohort="Cohort 2",
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
        cohort="Cohort 3",
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
        cohort="Cohort 4",
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
        cohort="Cohort 5",
    ),
]

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
        cohort="Cohort 1",
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
        cohort="Cohort 2",
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
        cohort="Cohort 3",
    ),
]


def test_process():
    """Assigns leaders for team placement."""
    # define targets
    people = assign_leaders(PEOPLE, TEAMS)
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 3
    assert len([x for x in people if x.team == "Team A"]) == 2
    assert len([x for x in people if x.team == "Team B"]) == 2
    assert len([x for x in people if x.team == ""]) == 1


def test_invalid_team_names():
    people_2 = assign_leaders(PEOPLE2, TEAMS)
    cohorts = list(set([x.cohort for x in people_2]))
    assert len(cohorts) == 3
    assert len([x for x in people_2 if x.team == "Team A"]) == 0
    assert len([x for x in people_2 if x.team == "Team B"]) == 0

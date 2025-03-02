# third-party imports
import pytest

# external imports
from team_placement.algorithm.first_pass import first_pass
from team_placement.schemas import BooleanEnum, Collective, Gender, Person


@pytest.fixture
def people_regular() -> list[Person]:
    # person with one preferred person must be assigned to same cohort
    # extra person must be assigned once cohorts consolidate
    return [
        Person(
            index="New Person",
            order=1,
            firstName="John",
            lastName="Doe",
            age=25,
            gender=Gender.male,
            firstTime=BooleanEnum.yes,
            collective=Collective.new,
            leader=BooleanEnum.no,
            participant=BooleanEnum.yes,
            preferredPeople=["Preferred Person"],
            cohort="Cohort 1",
        ),
        Person(
            index="Preferred Person",
            order=2,
            firstName="Jane",
            lastName="Doe",
            age=25,
            gender=Gender.female,
            firstTime=BooleanEnum.no,
            collective=Collective.new,
            leader=BooleanEnum.no,
            participant=BooleanEnum.yes,
            preferredPeople=[],
            cohort="Cohort 2",
        ),
        Person(
            index="Prefers Both People",
            order=3,
            firstName="Extra",
            lastName="Doe",
            age=25,
            gender=Gender.male,
            firstTime=BooleanEnum.yes,
            collective=Collective.new,
            leader=BooleanEnum.no,
            participant=BooleanEnum.yes,
            preferredPeople=["New Person", "Preferred Person"],
            cohort="Cohort 3",
        ),
    ]


@pytest.fixture
def people_leader_conflict() -> list[Person]:
    # new person will get their choice and new leader will not based on order
    return [
        Person(
            index="New Person",
            order=1,
            firstName="John",
            lastName="Doe",
            age=25,
            gender=Gender.male,
            firstTime=BooleanEnum.yes,
            collective=Collective.new,
            leader=BooleanEnum.no,
            participant=BooleanEnum.yes,
            preferredPeople=["Preferred Leader"],
            cohort="Cohort 1",
        ),
        Person(
            index="New Leader",
            order=2,
            firstName="Jane",
            lastName="Doe",
            age=25,
            gender=Gender.female,
            firstTime=BooleanEnum.yes,
            collective=Collective.new,
            leader=BooleanEnum.yes,
            participant=BooleanEnum.yes,
            team="Team A",
            preferredPeople=["New Person"],
            cohort="Team A",
        ),
        Person(
            index="Preferred Leader",
            order=3,
            firstName="Leader",
            lastName="Doe",
            age=25,
            gender=Gender.male,
            firstTime=BooleanEnum.no,
            collective=Collective.new,
            leader=BooleanEnum.yes,
            participant=BooleanEnum.yes,
            team="Team B",
            preferredPeople=[],
            cohort="Team B",
        ),
    ]


def test_process(people_regular: list[Person]):
    """Tests that the first pass assigns people to teams."""
    people = first_pass(people_regular)
    assert len(list(set([x.cohort for x in people]))) == 1


def test_leader_conflict(people_leader_conflict: list[Person]):
    """Tests that the first pass assigns people to teams."""
    people = first_pass(people_leader_conflict)
    assert len(list(set([x.cohort for x in people]))) == 2
    assert len([x for x in people if x.team == "Team A"]) == 1
    assert len([x for x in people if x.team == "Team B"]) == 2

# external imports
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.objects import PersonObject
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, Team

TEAMS = [Team(index="Team 1", name="Team A"), Team(index="Team 2", name="Team B")]

# person with one preferred person must be assigned to same cohort
# extra person must be assigned once cohorts consolidate
PEOPLE_REGULAR = [
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
    ),
]
PEOPLE_REGULAR = [PersonObject(x) for x in PEOPLE_REGULAR]
for person in PEOPLE_REGULAR:
    person.preferred = [x for x in PEOPLE_REGULAR if x.index in person.preferred_people]

# new person will get their choice and new leader will not based on order
PEOPLE_LEADER_CONFLICT = [
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
    ),
]
PEOPLE_LEADER_CONFLICT = [PersonObject(x) for x in PEOPLE_LEADER_CONFLICT]
for person in PEOPLE_LEADER_CONFLICT:
    person.preferred = [
        x for x in PEOPLE_LEADER_CONFLICT if x.index in person.preferred_people
    ]


def test_process():
    """Tests that the first pass assigns people to teams."""
    cohorts = [x.cohort for x in PEOPLE_REGULAR]
    _, cohorts = first_pass(PEOPLE_REGULAR, cohorts)
    assert len(cohorts) == 1

    cohorts = [x.cohort for x in PEOPLE_LEADER_CONFLICT]
    _, cohorts = first_pass(PEOPLE_LEADER_CONFLICT, cohorts)
    assert len(cohorts) == 2
    cohort_A = next(iter([x for x in cohorts if x.team == "Team A"]), None)
    assert cohort_A is not None and len(cohort_A.people) == 1
    cohort_B = next(iter([x for x in cohorts if x.team == "Team B"]), None)
    assert cohort_B is not None and len(cohort_B.people) == 2

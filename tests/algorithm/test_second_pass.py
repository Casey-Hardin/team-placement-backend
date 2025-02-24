# external imports
from team_placement.algorithm.second_pass import second_pass
from team_placement.algorithm.objects import Cohort, PersonObject
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
    Team(index="Team 3", name="Team C"),
    Team(index="Team 4", name="Team D"),
]

# base set of people where modifications are made to test different scenarios
# all changes are made to the preferred people of the first person (New Girl)
PEOPLE_BASE = [
    Person(
        index="New Girl",
        order=1,
        firstName="Jane",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Girl 1",
        order=2,
        firstName="Jill",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Girl 2",
        order=3,
        firstName="Julia",
        lastName="Doe",
        age=23,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Extra Girl",
        order=4,
        firstName="June",
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
        index="Extra Guy 1",
        order=5,
        firstName="John",
        lastName="Doe",
        age=23,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Extra Guy 2",
        order=6,
        firstName="Jake",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Extra Guy 3",
        order=7,
        firstName="Jude",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
    Person(
        index="Extra Guy 4",
        order=8,
        firstName="Jeff",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
    ),
]

# neither person meets targets - assign Girl 1 who is closer in age
PEOPLE_1 = list(PEOPLE_BASE)
PEOPLE_1[0].preferredPeople = ["Girl 2", "Girl 1"]
PEOPLE_1 = [PersonObject(x) for x in PEOPLE_1]
for person in PEOPLE_1:
    person.preferred = [x for x in PEOPLE_1 if x.index in person.preferred_people]

# one person meets targets - assign Extra Guy 1 who meets targets
PEOPLE_2 = list(PEOPLE_BASE)
PEOPLE_2[0].preferredPeople = ["Girl 1", "Extra Guy 1"]
PEOPLE_2 = [PersonObject(x) for x in PEOPLE_2]
for person in PEOPLE_2:
    person.preferred = [x for x in PEOPLE_2 if x.index in person.preferred_people]

# two people meet targets - assign neither as must assign is False
PEOPLE_3 = list(PEOPLE_BASE)
PEOPLE_3[0].preferredPeople = ["Extra Guy 1", "Extra Guy 3"]
PEOPLE_3 = [PersonObject(x) for x in PEOPLE_3]
for person in PEOPLE_3:
    person.preferred = [x for x in PEOPLE_3 if x.index in person.preferred_people]

# two people meet targets
# assign Extra Guy 3 as must assign is True and he is closer in age to New Girl
PEOPLE_4 = list(PEOPLE_BASE)
PEOPLE_4[0].preferredPeople = ["Extra Guy 1", "Extra Guy 3"]
PEOPLE_4 = [PersonObject(x) for x in PEOPLE_4]
for person in PEOPLE_4:
    person.preferred = [x for x in PEOPLE_4 if x.index in person.preferred_people]

TARGETS = Targets(
    team_size=2,
    collective_new=1,
    collective_newish=0,
    collective_oldish=0,
    collective_old=1,
    age_std=2,
    girl_count=1,
)


def test_neither_meets_targets():
    """
    Tests the second pass when neither preferred person meets targets.
    Assigns the prioritized cohort.
    """
    cohorts = [x.cohort for x in PEOPLE_1]
    new_people_left = [x for x in PEOPLE_1 if x.first_time == BooleanEnum.yes]
    new_people_left, cohorts = second_pass(
        new_people_left, cohorts, TARGETS, len(TEAMS)
    )

    assert len(new_people_left) == 0
    assert len(cohorts) == 7
    new_cohort = next(
        iter([x for x in cohorts if "New Girl" in [y.index for y in x.people]]), None
    )
    assert new_cohort is not None
    assert "Girl 1" in [x.index for x in new_cohort.people]


def test_one_meets_targets():
    """
    Tests the second pass when only one preferred person meets targets.
    Assigns the person that meets targets.
    """
    cohorts = [x.cohort for x in PEOPLE_2]
    new_people_left = [x for x in PEOPLE_2 if x.first_time == BooleanEnum.yes]
    new_people_left, cohorts = second_pass(
        new_people_left, cohorts, TARGETS, len(TEAMS)
    )

    assert len(new_people_left) == 0
    assert len(cohorts) == 7
    new_cohort = next(
        iter([x for x in cohorts if "New Girl" in [y.index for y in x.people]]), None
    )
    assert new_cohort is not None
    assert "Extra Guy 1" in [x.index for x in new_cohort.people]


def test_two_meet_targets():
    """
    Tests the second pass when both preferred people meet targets without must assign.
    No one is assigned.
    """
    cohorts = [x.cohort for x in PEOPLE_3]
    cohorts_initial = [x.cohort.to_list() for x in PEOPLE_3]
    new_people_left = [x for x in PEOPLE_3 if x.first_time == BooleanEnum.yes]
    new_people_left, cohorts = second_pass(
        new_people_left, cohorts, TARGETS, len(TEAMS)
    )

    assert len(new_people_left) == 1
    assert len(cohorts) == 8
    assert [x.cohort.to_list() for x in PEOPLE_3] == cohorts_initial


def test_two_meet_targets_must_assign():
    """
    Tests the second pass when both preferred people meet targets with must assign.
    Assigns the prioritized cohort.
    """
    cohorts = [x.cohort for x in PEOPLE_4]
    new_people_left = [x for x in PEOPLE_4 if x.first_time == BooleanEnum.yes]
    new_people_left, cohorts = second_pass(
        new_people_left, cohorts, TARGETS, len(TEAMS), True
    )

    assert len(new_people_left) == 0
    assert len(cohorts) == 7
    new_cohort = next(
        iter([x for x in cohorts if "New Girl" in [y.index for y in x.people]]), None
    )
    assert new_cohort is not None
    assert "Extra Guy 1" not in [x.index for x in new_cohort.people]
    assert "Extra Guy 3" in [x.index for x in new_cohort.people]

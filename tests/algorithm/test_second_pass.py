# native imports
from copy import deepcopy

# external imports
from team_placement.algorithm.second_pass import second_pass
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
        cohort="Cohort 1",
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
        cohort="Cohort 2",
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
        cohort="Cohort 3",
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
        cohort="Cohort 4",
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
        cohort="Cohort 5",
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
        cohort="Cohort 6",
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
        cohort="Cohort 7",
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
        cohort="Cohort 8",
    ),
]

# neither person meets targets - assign Girl 1 who is closer in age
PEOPLE_1 = deepcopy(PEOPLE_BASE)
PEOPLE_1[0].preferredPeople = ["Girl 2", "Girl 1"]

# one person meets targets - assign Extra Guy 1 who meets targets
PEOPLE_2 = deepcopy(PEOPLE_BASE)
PEOPLE_2[0].preferredPeople = ["Girl 1", "Extra Guy 1"]

# two people meet targets - assign neither as must assign is False
PEOPLE_3 = deepcopy(PEOPLE_BASE)
PEOPLE_3[0].preferredPeople = ["Extra Guy 1", "Extra Guy 3"]

# two people meet targets
# assign Extra Guy 3 as must assign is True and he is closer in age to New Girl
PEOPLE_4 = deepcopy(PEOPLE_BASE)
PEOPLE_4[0].preferredPeople = ["Extra Guy 1", "Extra Guy 3"]

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
    people = second_pass(PEOPLE_1, TARGETS, len(TEAMS))
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 7
    new_girl = next(iter([x for x in people if x.index == "New Girl"]), None)
    girl_1 = next(iter([x for x in people if x.index == "Girl 1"]), None)
    assert new_girl is not None and girl_1 is not None
    assert new_girl.cohort == girl_1.cohort


def test_one_meets_targets():
    """
    Tests the second pass when only one preferred person meets targets.
    Assigns the person that meets targets.
    """
    people = second_pass(PEOPLE_2, TARGETS, len(TEAMS))
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 7
    new_girl = next(iter([x for x in people if x.index == "New Girl"]), None)
    extra_guy = next(iter([x for x in people if x.index == "Extra Guy 1"]), None)
    assert new_girl is not None and extra_guy is not None
    assert new_girl.cohort == extra_guy.cohort


def test_two_meet_targets():
    """
    Tests the second pass when both preferred people meet targets without must assign.
    No one is assigned.
    """
    people_in_cohorts = [
        [x for x in PEOPLE_3 if x.cohort == cohort]
        for cohort in set([x.cohort for x in PEOPLE_3])
    ]
    people_in_cohorts.sort(key=lambda x: min(x, key=lambda y: y.order).order)
    cohorts_initial = [
        [str(person) for person in cohort] for cohort in people_in_cohorts
    ]

    people = second_pass(PEOPLE_3, TARGETS, len(TEAMS))
    cohorts = list(set([x.cohort for x in people]))

    people_in_cohorts = [
        [x for x in people if x.cohort == cohort]
        for cohort in set([x.cohort for x in people])
    ]
    people_in_cohorts.sort(key=lambda x: min(x, key=lambda y: y.order).order)

    assert len(cohorts) == 8
    assert [
        [str(person) for person in cohort] for cohort in people_in_cohorts
    ] == cohorts_initial


def test_two_meet_targets_must_assign():
    """
    Tests the second pass when both preferred people meet targets with must assign.
    Assigns the prioritized cohort.
    """
    people = second_pass(PEOPLE_4, TARGETS, len(TEAMS), True)
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 7
    new_girl = next(iter([x for x in people if x.index == "New Girl"]), None)
    extra_guy_1 = next(iter([x for x in people if x.index == "Extra Guy 1"]), None)
    extra_guy_3 = next(iter([x for x in people if x.index == "Extra Guy 3"]), None)
    assert new_girl is not None and extra_guy_1 is not None and extra_guy_3 is not None
    assert new_girl.cohort != extra_guy_1.cohort
    assert new_girl.cohort == extra_guy_3.cohort

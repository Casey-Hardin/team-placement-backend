# native imports
from copy import deepcopy

# external imports
from team_placement.algorithm.sift_cohorts import sift_cohorts
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
]

# base set of people where modifications are made to test different scenarios
# all changes are made to the preferred people of the first person (New Girl)
PEOPLE_BASE = [
    Person(
        index="Girl 1",
        order=1,
        firstName="Jane",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 1",
    ),
    Person(
        index="Girl 2",
        order=2,
        firstName="June",
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
        index="Girl 3",
        order=3,
        firstName="Julia",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 3",
    ),
    Person(
        index="Girl 4",
        order=4,
        firstName="Jaylynn",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 4",
    ),
    Person(
        index="Girl 5",
        order=5,
        firstName="Jillian",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 5",
    ),
    Person(
        index="Girl 6",
        order=6,
        firstName="Juniper",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 6",
    ),
    Person(
        index="Guy 1",
        order=7,
        firstName="John",
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
        index="Guy 2",
        order=8,
        firstName="Jeff",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 8",
    ),
    Person(
        index="Guy 3",
        order=9,
        firstName="Jack",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.old,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 9",
    ),
]


# no cohort meets targets - combine with best option (Team B) based on targets
PEOPLE_1 = deepcopy(PEOPLE_BASE)
PEOPLE_1[0].leader = BooleanEnum.yes
PEOPLE_1[0].team = "Team A"
PEOPLE_1[0].age = 23
PEOPLE_1[1].leader = BooleanEnum.yes
PEOPLE_1[1].team = "Team B"
PEOPLE_1[2].leader = BooleanEnum.yes
PEOPLE_1[2].team = "Team C"
PEOPLE_1[2].age = 23
PEOPLE_1[3].cohort = "Preset Cohort"
PEOPLE_1[4].cohort = "Preset Cohort"

# one leader cohort meets targets - assign to Team C
PEOPLE_2 = deepcopy(PEOPLE_BASE)
PEOPLE_2[0].leader = BooleanEnum.yes
PEOPLE_2[0].team = "Team A"
PEOPLE_2[1].leader = BooleanEnum.yes
PEOPLE_2[1].team = "Team B"
PEOPLE_2[6].leader = BooleanEnum.yes
PEOPLE_2[6].team = "Team C"
PEOPLE_2[2].cohort = "Preset Cohort"
PEOPLE_2[3].cohort = "Preset Cohort"

# two leader cohorts meet targets - assign neither
PEOPLE_3 = deepcopy(PEOPLE_BASE)
PEOPLE_3[6].leader = BooleanEnum.yes
PEOPLE_3[6].team = "Team A"
PEOPLE_3[7].leader = BooleanEnum.yes
PEOPLE_3[7].team = "Team B"
PEOPLE_3[2].cohort = "Preset Cohort"
PEOPLE_3[3].cohort = "Preset Cohort"

# no cohort meets targets - assign to unassigned Team C
PEOPLE_4 = deepcopy(PEOPLE_BASE)
PEOPLE_4[0].leader = BooleanEnum.yes
PEOPLE_4[0].team = "Team A"
PEOPLE_4[1].leader = BooleanEnum.yes
PEOPLE_4[1].team = "Team B"
PEOPLE_4[2].cohort = "Preset Cohort"
PEOPLE_4[3].cohort = "Preset Cohort"

TARGETS = Targets(
    team_size=3,
    collective_new=0,
    collective_newish=0,
    collective_oldish=0,
    collective_old=3,
    age_std=2,
    girl_count=2,
)


def test_neither_meets_targets():
    """
    Tests sifting cohorts when no leader cohort meets targets.
    Assigns the prioritized cohort.
    """
    people = sift_cohorts(PEOPLE_1, TARGETS, TEAMS)
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 7
    girl_4 = next(iter([x for x in people if x.index == "Girl 4"]), None)
    assert girl_4 is not None
    assert girl_4.team == "Team B"


def test_one_meets_targets():
    """
    Tests sifting cohorts when only one leader cohort meets targets.
    Assigns the leader cohort that meets targets.
    """
    people = sift_cohorts(PEOPLE_2, TARGETS, TEAMS)
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 7
    girl_3 = next(iter([x for x in people if x.index == "Girl 3"]), None)
    assert girl_3 is not None
    assert girl_3.team == "Team C"


def test_two_meet_targets():
    """
    Tests sifting cohorts when multiple leader cohorts meet targets.
    No assignments.
    """
    people_in_cohorts = [
        [x for x in PEOPLE_3 if x.cohort == cohort]
        for cohort in set([x.cohort for x in PEOPLE_3])
    ]
    people_in_cohorts.sort(key=lambda x: min(x, key=lambda y: y.order).order)
    cohorts_initial = [
        [str(person) for person in cohort] for cohort in people_in_cohorts
    ]

    people = sift_cohorts(PEOPLE_3, TARGETS, TEAMS)

    people_in_cohorts = [
        [x for x in people if x.cohort == cohort]
        for cohort in set([x.cohort for x in people])
    ]
    people_in_cohorts.sort(key=lambda x: min(x, key=lambda y: y.order).order)

    assert [
        [str(person) for person in cohort] for cohort in people_in_cohorts
    ] == cohorts_initial


def test_available_team():
    """
    Tests sifting cohorts when no leader cohorts meet targets
    but there is an available team.
    Assigns cohort to the available team.
    """
    people = sift_cohorts(PEOPLE_4, TARGETS, TEAMS)
    cohorts = list(set([x.cohort for x in people]))

    assert len(cohorts) == 8
    girl_3 = next(iter([x for x in people if x.index == "Girl 3"]), None)
    assert girl_3 is not None
    assert girl_3.team == "Team C"

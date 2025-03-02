# external imports
from team_placement.algorithm.apply_controls import apply_controls
from team_placement.schemas import (
    BooleanEnum,
    Collective,
    Control,
    Gender,
    Person,
    Team,
)


TEAMS = [Team(index="Team 1", name="Team A"), Team(index="Team 2", name="Team B")]


# people to be assigned based on people controls
PEOPLE = [
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
        preferredPeople=["Preferred Person", "Random Person"],
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
        index="Exclude Person",
        order=3,
        firstName="Exclude",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 3",
    ),
    Person(
        index="Leader 1",
        order=4,
        firstName="Leonard",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team A",
        preferredPeople=[],
        cohort="Team A",
    ),
    Person(
        index="Leader 2",
        order=5,
        firstName="Leslie",
        lastName="Doe",
        age=25,
        gender=Gender.female,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="Team B",
        preferredPeople=[],
        cohort="Team B",
    ),
    Person(
        index="Include Team A Person",
        order=6,
        firstName="Laina",
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
        index="Another New Person",
        order=7,
        firstName="Charles",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[
            "Another Preferred Person",
            "Another Exclude Person",
        ],
        cohort="Cohort 5",
    ),
    Person(
        index="Another Preferred Person",
        order=8,
        firstName="Charlie",
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
        index="Another Exclude Person",
        order=9,
        firstName="Danny",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.no,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        preferredPeople=[],
        cohort="Cohort 7",
    ),
]

CONTROLS = [
    Control(
        index="Control 1",
        order=1,
        personIndex="Preferred Person",
        teamInclude=["New Person"],
        teamExclude=["Exclude Person"],
        roomInclude=[],
        roomExclude=[],
    ),
    Control(
        index="Control 2",
        order=2,
        personIndex="Include Team A Person",
        teamInclude=["Leader 1"],
        teamExclude=[],
        roomInclude=[],
        roomExclude=[],
    ),
    Control(
        index="Ignored Control",
        order=3,
        personIndex="Include Team A Person",
        teamInclude=["Leader 2"],
        teamExclude=[],
        roomInclude=[],
        roomExclude=[],
    ),
    Control(
        index="Control 4",
        order=4,
        personIndex="Another New Person",
        teamInclude=[],
        teamExclude=["Another Exclude Person"],
        roomInclude=[],
        roomExclude=[],
    ),
]


def test_process():
    """Tests that the first pass assigns people to teams."""
    people = apply_controls(PEOPLE, CONTROLS)
    cohorts = list(set([x.cohort for x in PEOPLE]))
    for new_person in [x for x in people if x.firstTime == BooleanEnum.yes]:
        assert len([x for x in people if x.cohort == new_person.cohort]) > 1
    assert len(cohorts) == 6

    new_person = next(iter([x for x in people if x.index == "New Person"]), None)
    preferred_person = next(
        iter([x for x in people if x.index == "Preferred Person"]), None
    )
    exclude_person = next(
        iter([x for x in people if x.index == "Exclude Person"]), None
    )
    include_person = next(
        iter([x for x in people if x.index == "Include Team A Person"]), None
    )
    leader_1_person = next(iter([x for x in PEOPLE if x.index == "Leader 1"]), None)
    another_new_person = next(
        iter([x for x in people if x.index == "Another New Person"]), None
    )
    another_preferred_person = next(
        iter([x for x in people if x.index == "Another Preferred Person"]), None
    )
    another_exclude_person = next(
        iter([x for x in people if x.index == "Another Exclude Person"]), None
    )
    assert all(
        [
            x is not None
            for x in [
                new_person,
                preferred_person,
                exclude_person,
                include_person,
                leader_1_person,
                another_new_person,
                another_preferred_person,
                another_exclude_person,
            ]
        ]
    )

    for cohort in cohorts:
        if new_person.cohort == cohort:
            assert preferred_person.cohort == cohort
            assert exclude_person.index in new_person.banned_people
        if include_person.cohort == cohort:
            assert leader_1_person.cohort == cohort
            assert include_person.team == "Team A"
        if another_new_person.cohort == cohort:
            assert another_preferred_person.cohort == cohort
            assert another_exclude_person.index in another_new_person.banned_people

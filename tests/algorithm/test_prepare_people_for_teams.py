# external imports
from team_placement.algorithm.objects import PersonObject
from team_placement.algorithm.prepare_people_for_teams import prepare_people_for_teams
from team_placement.schemas import BooleanEnum, Collective, Gender, Person

PEOPLE = [
    Person(
        index="Attendee",
        order=1,
        firstName="John",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
        team="A Team",
    ),
    Person(
        index="Leader",
        order=2,
        firstName="John",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.yes,
        participant=BooleanEnum.yes,
        team="B Team",
    ),
    Person(
        index="Non-Participant",
        order=3,
        firstName="John",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.no,
    ),
]


def test_process():
    """Tests that people are prepared for team placement."""
    # prepare people
    people = prepare_people_for_teams(PEOPLE)

    # attendee must be found and have no team
    attendee = next(iter([x for x in people if x.index == "Attendee"]), None)
    assert attendee is not None
    assert attendee.team == ""

    # leader must be found and have a team
    first_leader = next(iter([x for x in PEOPLE if x.index == "Leader"]), None)
    leader = next(iter([x for x in people if x.index == "Leader"]), None)
    assert leader is not None and first_leader is not None
    assert leader.team == first_leader.team

    # non-participants are not considered for team placement
    non_participant = next(
        iter([x for x in people if x.index == "Non-Participant"]), None
    )
    assert non_participant is None

    # all remaining people must be of class PersonObject
    for person in people:
        assert type(person) == PersonObject
        assert all([type(x) == PersonObject for x in person.preferred])

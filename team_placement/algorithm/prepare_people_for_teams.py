# external imports
from team_placement.algorithm.objects import PersonObject
from team_placement.schemas import BooleanEnum, Person


def prepare_people_for_teams(all_people: list[Person]) -> list[PersonObject]:
    """
    Prepares people for team placement.

    Parameters
    ----------
    all_people
        People defined from the interface.

    Returns
    -------
    list[PersonObject]
        People objects prepared for team placement.
    """
    # reset team for people who are not leaders
    for person in all_people:
        if person.team != "" and person.leader != BooleanEnum.yes:
            person.team = ""

    # remove people who don't participate on teams
    non_participant_indices = [
        x.index for x in all_people if x.participant == BooleanEnum.no
    ]
    people = [x for x in all_people if x.participant == BooleanEnum.yes]
    for person in people:
        person.preferredPeople = [
            x for x in person.preferredPeople if x not in non_participant_indices
        ]

    # convert Person models to PersonObject objects
    people = [PersonObject(person) for person in people]
    for person in people:
        person.preferred = [x for x in people if x.index in person.preferred_people]
    return people

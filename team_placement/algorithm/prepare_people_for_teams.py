# native imports
import shortuuid

# external imports
from team_placement.constants import MAXIMUM_AGE, MINIMUM_AGE
from team_placement.schemas import BooleanEnum, Person


def prepare_people_for_teams(all_people: list[Person]) -> list[Person]:
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

    # adjust age if invalid
    for person in people:
        if person.age < MINIMUM_AGE:
            ages = [x.age for x in people if x.index in person.preferredPeople]
            estimated_age = (MINIMUM_AGE + MAXIMUM_AGE) / 2
            if len(ages) > 0:
                estimated_age = sum(ages) / len(ages)
                if estimated_age < MINIMUM_AGE or estimated_age > MAXIMUM_AGE:
                    estimated_age = sum(ages) / len(ages)
            person.age = int(estimated_age)
        elif person.age > MAXIMUM_AGE:
            person.age = MAXIMUM_AGE

    # assign people to cohorts
    for person in people:
        person.cohort = shortuuid.ShortUUID().random(length=6)
    return people

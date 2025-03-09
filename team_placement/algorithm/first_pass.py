# external imports
from team_placement.schemas import Person
from team_placement.utils.helpers import find_friends, find_new_people, join_cohorts


def first_pass(people: list[Person]) -> list[Person]:
    """
    Assigns people to cohorts with 1 preferred person.
    Recurses after each addition to collapse preferred people on cohorts.

    Parameters
    ----------
    people
        Already existing people where cohorts are assigned.

    Returns
    -------
    list[Person]
        People with new people added to cohorts.
    """
    # assign new people to cohorts
    new_people = find_new_people(people)
    for person in new_people:
        # find friends
        friends = find_friends(person, people)

        # take action when a new person has 0 or 1 possible preference
        match len(friends):
            case 0:
                # no friends to add
                continue
            case 1:
                # add friend to the cohort of the person
                people = join_cohorts(person.cohort, friends[0].cohort, people)

                # recurse
                return first_pass(people)
            case _:
                # too many choices at this time
                continue
    return people

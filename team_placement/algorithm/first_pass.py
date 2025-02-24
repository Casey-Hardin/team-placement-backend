from team_placement.algorithm.objects import Cohort, PersonObject


def first_pass(
    people: list[PersonObject], cohorts: list[Cohort]
) -> tuple[list[PersonObject], list[Cohort]]:
    """
    Assigns people to cohorts with 1 preferred person.
    Recurses after each addition to collapse preferred people on cohorts.

    Parameters
    ----------
    people
        People to be added to cohorts.
    cohorts
        Already existing cohorts.

    Returns
    -------
    list[PersonObject]
        People with teams assigned.
    list[Cohort]
        Cohorts with new people added.
    """
    current_people = list(people)
    for person in current_people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        friend_cohorts = list(
            set(
                [
                    x.cohort
                    for x in person.preferred
                    if x not in person.cohort.people
                    and (person.team == "" or x.team == "")
                    and x not in person.cohort.banned_people
                ]
            )
        )

        # take action when a new person has 0 or 1 possible preference
        match len(friend_cohorts):
            case 0:
                # no new friends to add
                # remove the person from the list
                people = [x for x in people if x != person]
                continue
            case 1:
                # this is the person's choice
                friend_cohort = friend_cohorts[0]
            case _:
                # too many choices at this time
                continue

        # combine cohorts of person and their friend
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # recurse
        people = [x for x in people if x != person]
        return first_pass(people, cohorts)
    return people, cohorts

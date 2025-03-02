# external imports
from team_placement.schemas import Person, Targets
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.prioritized_friend import prioritized_friend
from team_placement.utils.helpers import (
    find_friends,
    find_friends_strict,
    find_new_people,
    join_cohorts,
)


def second_pass(
    people: list[Person],
    targets: Targets,
    team_count: int,
    must_assign: bool = False,
) -> list[Person]:
    """
    Assigns people to cohorts based on their demographics and preferences.

    Parameters
    ----------
    people
        All people to assign to teams.
    targets
        Targets for each cohort.
    team_count
        Number of teams to create.
    must_assign
        Flag to force assignment of people to cohorts.

    Returns
    -------
    list[Person]
        People with cohorts assigned.
    """
    # find new friends for each person to assign
    new_people = find_new_people(people)
    for person in new_people:
        # find friends
        friends = find_friends(person, people)

        # find new friends based on targets
        strict_friends = find_friends_strict(
            person, friends, people, targets, team_count
        )

        # take action when a new person has 0 or 1 possible preferences
        match len(strict_friends):
            case 0:
                # adding person to a cohort with any of their friends
                # will exceed targets
                friend = prioritized_friend(
                    person, friends, people, targets, team_count
                )
            case 1:
                # this is the person's choice
                friend = strict_friends[0]
            case _:
                # 2+ people are reasonable additions
                # too many choices at this time
                if not must_assign:
                    continue

                friend = prioritized_friend(
                    person, strict_friends, people, targets, team_count
                )

        # no new friends found
        if friend is None:
            continue

        # combine person and their friend's cohorts
        people = join_cohorts(person.cohort, friend.cohort, people)

        # recurse
        people = first_pass(people)
        people = second_pass(people, targets, team_count)
        if must_assign:
            people = second_pass(people, targets, team_count, must_assign=must_assign)
        return people
    return people

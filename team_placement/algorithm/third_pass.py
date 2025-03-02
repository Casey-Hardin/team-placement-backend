# external imports
from team_placement.algorithm.prioritized_friend import prioritized_friend
from team_placement.algorithm.sift_cohorts import sift_cohorts
from team_placement.schemas import Person, Targets, Team
from team_placement.utils.helpers import (
    find_friends,
    find_friends_strict,
    find_new_people_complete,
    join_cohorts,
    list_cohorts,
)


def third_pass(
    people: list[Person],
    targets: Targets,
    teams: list[Team],
) -> list[Person]:
    """
    Assigns people to cohorts based on their demographics and preferences.

    Parameters
    ----------
    people
        All people to assign to teams.
    targets
        Targets for each cohort.
    teams
        Teams for people assignment.

    Returns
    -------
    list[Person]
        People with cohorts assigned.
    """
    while True:
        print(len(list(set([x.cohort for x in people]))))
        people_in_cohorts = list_cohorts(people)

        indices = find_new_people_complete(people, targets, len(teams))
        for index in indices:
            # find person with friends to assign
            person = next(iter([x for x in people if x.index == index]), None)
            if person is None:
                continue

            # find friends
            friends = find_friends(person, people)

            # find new friends based on targets
            new_friends = find_friends_strict(
                person, friends, people, targets, len(teams)
            )

            # take action when a new person has 0 or 1 possible preferences remaining
            leader_cohorts = list(set([x.cohort for x in people if x.team != ""]))
            match len(new_friends):
                case 0:
                    # adding person to a cohort with any of their remaining friends
                    # will exceed targets
                    continue
                case 1:
                    # this is the person's choice
                    new_friend = new_friends[0]
                case _:
                    # 2+ people are reasonable additions
                    # assign the best choice for the cohort
                    new_friend = prioritized_friend(
                        person, new_friends, people, targets, leader_cohorts, len(teams)
                    )

            # no new friends found
            if new_friend is None:
                continue

            # combine person and their friend's cohorts
            people = join_cohorts(person.cohort, new_friend.cohort, people)

            # place cohorts with 0 or 1 possible to leader cohorts
            people = sift_cohorts(people, targets, teams)

        if list_cohorts(people) == people_in_cohorts:
            break
    return people

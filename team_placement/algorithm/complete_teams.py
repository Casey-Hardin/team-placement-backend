# external imports
from team_placement.algorithm.prioritized_friend import prioritized_friend
from team_placement.schemas import Person, Targets
from team_placement.utils.helpers import (
    collect_metrics,
    collect_representatives,
    join_cohorts,
)


def complete_teams(
    people: list[Person], targets: Targets, team_count: int
) -> list[Person]:
    """
    Assigns cohorts to teams based on their size and preferences.

    Parameters
    ----------
    people
        All people to assign to teams.
    targets
        Targets for each cohort.
    team_count
        Number of teams to assign people to.

    Returns
    -------
    list[Person]
        People with teams assigned.
    """
    # complete teams based on preferences in order of cohort size
    representatives = collect_representatives(people)
    representatives.sort(
        key=lambda x: len([y for y in people if y.cohort == x.cohort]), reverse=True
    )

    leaders = [x for x in representatives if x.team != ""]
    remaining_representatives = [x for x in representatives if x.team == ""]

    tolerance = 2
    min_allowed = targets.team_size - tolerance
    min_allowed = min_allowed if min_allowed > 0 else 0
    priority = "team_size"
    for person in remaining_representatives:
        number_assigned = (
            sum([getattr(collect_metrics(people, x.cohort), priority) for x in leaders])
            - min_allowed * team_count
        )
        number_left = (
            getattr(targets, priority) * team_count
            - number_assigned
            - min_allowed * team_count
        )
        max_value = min(
            getattr(collect_metrics(people, person.cohort), priority) + number_left,
            getattr(targets, priority) + tolerance,
        )

        # minimum value must be maintained
        max_value = max_value if max_value > min_allowed else min_allowed

        # leaders of cohorts that are not at or above the maximum team size
        valid_leaders = [
            x
            for x in leaders
            if getattr(collect_metrics(people, x.cohort), priority) < max_value
        ]
        if len(valid_leaders) == 0:
            continue

        # find the best leader for the person
        friend = prioritized_friend(person, valid_leaders, people, targets, team_count)
        if friend is None:
            continue

        # combine person and their friend's cohorts
        people = join_cohorts(person.cohort, friend.cohort, people)

    # assign remaining representatives to teams
    remaining_representatives = [x for x in people if x.team == ""]
    for person in remaining_representatives:
        # find the best leader for the person
        friend = prioritized_friend(person, leaders, people, targets, team_count)
        if friend is None:
            continue

        # combine person and their friend's cohorts
        people = join_cohorts(person.cohort, friend.cohort, people)
    return people

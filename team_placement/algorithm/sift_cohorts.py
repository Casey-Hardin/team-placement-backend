# external imports
from team_placement.algorithm.prioritized_friend import prioritized_friend
from team_placement.constants import PRIORITIES
from team_placement.schemas import Person, Targets, Team
from team_placement.utils.helpers import (
    collect_metrics,
    collect_representatives,
    find_friends_strict,
    join_cohorts,
    list_cohorts,
)


def sift_cohorts(
    people: list[Person],
    targets: Targets,
    teams: list[Team],
) -> list[Person]:
    """
    Assigns cohorts to leader cohorts based on targets.

    Parameters
    ----------
    people
        People to assign to teams.
    targets
        Targets for each cohort.
    teams
        Teams for cohort assignment.

    Returns
    -------
    list[Person]
        People after cohort assignment.
    """
    # used for comparison to determine if any cohorts are combined
    previous_cohorts = list_cohorts(people)

    # combine cohorts based on targets and sort by cohort size
    representatives = collect_representatives(people)
    representatives.sort(
        key=lambda x: len([y for y in people if y.cohort == x.cohort]), reverse=True
    )
    for person in representatives:
        # ignore leader cohorts
        if person.team != "":
            continue

        # collect leaders
        leaders = [x for x in people if x.team != ""]

        # determine if cohorts are sufficiently small to stop sifting
        gaurenteed = []
        leader_cohorts = list(set([x.cohort for x in leaders]))
        for cohort in leader_cohorts:
            leader_metrics = collect_metrics(people, cohort)
            min_condition = min(
                [
                    getattr(targets, priority) - getattr(leader_metrics, priority)
                    for priority in PRIORITIES
                    if priority != "age_std"
                ]
            )
            if len([x for x in people if x.cohort == cohort]) < min_condition:
                gaurenteed += cohort

        if len(gaurenteed) == 2:
            break

        # collect teams without members
        available_teams = [
            x.name for x in teams if x.name not in [y.team for y in people]
        ]

        # find leader cohorts that can be combined with this cohort while meeting targets
        valid_leaders = find_friends_strict(
            person, leaders, people, targets, len(teams)
        )
        match len(valid_leaders):
            case 0:
                # assign to a new team if allowed
                if len(available_teams) > 0:
                    for member in [x for x in people if x.cohort == person.cohort]:
                        member.team = available_teams[0]
                    continue

                # cohort cannot be combined with any leader cohorts
                # combine with best option based on targets
                best_leader = prioritized_friend(
                    person, leaders, people, targets, len(teams)
                )
            case 1:
                # a team is unavailable - too many choices at this time
                if len(available_teams) > 0:
                    continue

                # combine with leader cohort
                best_leader = valid_leaders[0]
            case _:
                # too many choices at this time
                continue

        # no leader found to cohort with while meeting targets
        if best_leader is None:
            continue

        # combine person and their friend's cohorts
        people = join_cohorts(person.cohort, best_leader.cohort, people)

    # restart if any cohorts are combined
    if previous_cohorts != list_cohorts(people):
        return sift_cohorts(people, targets, teams)
    return people

# external imports
from team_placement import schemas
from team_placement.algorithm.prioritized_cohorts import prioritized_cohort
from team_placement.algorithm.objects import Cohort


def sift_cohorts(
    cohorts: list[Cohort],
    targets: schemas.Targets,
    teams: list[schemas.Team],
) -> list[Cohort]:
    """
    Assigns cohorts to leader cohorts based on targets.

    Parameters
    ----------
    cohorts
        Cohorts to assign to leader cohorts.
    targets
        Targets for each cohort.
    teams
        Teams for cohort assignment.

    Returns
    -------
    list[Cohort]
        Cohorts after cohort assignment.
    """
    # used for comparison to determine if any cohorts are combined
    previous_cohorts = [x.to_list() for x in cohorts]

    # combine cohorts based on targets
    for cohort in cohorts:
        # leader cohorts cannot be combined
        if cohort.team != "":
            continue

        # collect leader cohorts
        leader_cohorts = [x for x in cohorts if x.team != ""]

        # collect teams without leaders
        available_teams = [
            x.name for x in teams if x.name not in [y.team for y in leader_cohorts]
        ]

        # find leader cohorts that can be combined with this cohort while meeting targets
        valid_leader_cohorts = [
            x
            for x in leader_cohorts
            if x.validate(targets, len(teams), cohorts, cohort)
        ]
        match len(valid_leader_cohorts):
            case 0:
                # assign to a new team if allowed
                if len(available_teams) > 0:
                    cohort.team = available_teams[0]
                    continue

                # cohort cannot be combined with any leader cohorts
                # combine with best option based on targets
                leader_cohort = prioritized_cohort(
                    cohort, leader_cohorts, targets, leader_cohorts
                )
            case 1:
                # a team is unavailable - too many choices at this time
                if len(available_teams) > 0:
                    continue

                # combine with leader cohort
                leader_cohort = valid_leader_cohorts[0]
            case _:
                # too many choices at this time
                continue

        # combine person and their friend's cohorts
        cohorts = leader_cohort.add(cohort, cohorts)

    # restart if any cohorts are combined
    if previous_cohorts != [x.to_list() for x in cohorts]:
        return sift_cohorts(cohorts, targets, teams)
    return cohorts

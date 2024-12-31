# external imports
from . import schemas
from team_placement.algorithm.objects import Cohort
from team_placement.algorithm.helpers import prioritized_cohort


def complete_teams(cohorts: list[Cohort], targets: schemas.Targets):
    # complete teams
    cohorts = sorted(cohorts, key=lambda x: x.team_size, reverse=True)
    remaining_cohorts = [x for x in cohorts if x.team_number is None]
    tolerance = 2
    all_leader_cohorts = [x for x in cohorts if x.team_number is not None]
    min_allowed = targets.team_size - tolerance
    min_allowed = min_allowed if min_allowed > 0 else 0
    for cohort in remaining_cohorts:
        number_assigned = sum(
            [x.team_size for x in all_leader_cohorts]
        ) - min_allowed * len(all_leader_cohorts)
        number_left = (
            targets.team_size * len(all_leader_cohorts)
            - number_assigned
            - min_allowed * len(all_leader_cohorts)
        )
        max_value = min(cohort.team_size + number_left, targets.team_size + tolerance)
        max_value = max_value if max_value > min_allowed else min_allowed
        leader_cohorts = sorted(
            [
                x
                for x in cohorts
                if x.team_number is not None and x.team_size < max_value
            ],
            key=lambda x: x.team_size,
            reverse=True,
        )
        if len(leader_cohorts) == 0:
            break

        selected_cohort = prioritized_cohort(
            cohort, leader_cohorts, targets, all_leader_cohorts
        )
        cohorts = selected_cohort.add(cohort, cohorts)

    leader_cohorts = [x for x in cohorts if x.team_number is not None]
    remaining_cohorts = [x for x in cohorts if x.team_number is None]
    for cohort in remaining_cohorts:
        selected_cohort = prioritized_cohort(
            cohort, leader_cohorts, targets, leader_cohorts
        )
        cohorts = selected_cohort.add(cohort, cohorts)
    return cohorts

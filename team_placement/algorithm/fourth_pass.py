# external imports
from team_placement.schemas import Targets
from team_placement.algorithm.objects import Cohort, Person
from team_placement.algorithm.third_pass import third_pass


def fourth_pass(
    people: list[Person],
    cohorts: list[Cohort],
    targets: Targets,
    previous_cohorts: list[list[str]],
) -> list[Cohort]:
    cohorts = third_pass(people, cohorts, targets)
    new_cohorts = [cohort.to_list() for cohort in cohorts]
    if new_cohorts == previous_cohorts:
        return cohorts
    return fourth_pass(people, cohorts, targets, list(new_cohorts))

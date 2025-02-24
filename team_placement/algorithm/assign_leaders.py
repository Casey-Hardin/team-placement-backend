# external imports
from team_placement.algorithm.objects import Cohort, PersonObject
from team_placement.schemas import Team


def assign_leaders(people: list[PersonObject], teams: list[Team]) -> list[Cohort]:
    """
    Assigns leaders to cohorts.

    Parameters
    ----------
    people
        People prepared for team placement.
    teams
        Teams defined in the interface.

    Returns
    -------
    list[Cohort]
        Cohorts with leaders of the same team in the same cohort.
    """
    # form functional groups to select teams
    cohorts = [x.cohort for x in people]

    # assign leaders to cohorts based on team
    for team in teams:
        leaders = [x for x in people if x.team == team.name]
        if len(leaders) == 0:
            continue

        pop_indices = []
        for index, cohort in enumerate(cohorts):
            if any([x in cohort.people for x in leaders]):
                pop_indices.append(index)
        cohorts = [x for x in cohorts if cohorts.index(x) not in pop_indices]
        cohorts.append(Cohort(leaders))
    return cohorts

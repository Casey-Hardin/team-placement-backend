# external imports
from team_placement.schemas import BooleanEnum, Person, Team


def assign_leaders(people: list[Person], teams: list[Team]) -> list[Person]:
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
    list[Person]
        People where leaders are placed on teams.
    """
    # assign leaders to cohorts based on team
    for team in teams:
        # assign leader to the same cohort
        leaders = [
            x for x in people if x.team == team.name and x.leader == BooleanEnum.yes
        ]
        for leader in leaders:
            leader.cohort = team.name
    return people

# external imports
from team_placement.algorithm.objects import PersonObject
from team_placement.schemas import Collective, Gender, Targets, Team


def define_targets(people: list[PersonObject], teams: list[Team]) -> Targets:
    """
    Defines targets for team placement optimization.

    people
        People to be placed on teams.
    teams
        Teams where people will be placed.

    Targets
        Goals for each team when placing people on teams.
    """
    # totals
    total_people = len(people)
    total_teams = len(teams)
    total_girls = len([x for x in people if x.gender == Gender.female])
    total_new = len([x for x in people if x.collective == Collective.new])
    total_newish = len([x for x in people if x.collective == Collective.newish])
    total_oldish = len([x for x in people if x.collective == Collective.oldish])
    total_old = len([x for x in people if x.collective == Collective.old])

    # targets per team
    return Targets(
        team_size=float(total_people / total_teams),
        collective_new=float(total_new / total_teams),
        collective_newish=float(total_newish / total_teams),
        collective_oldish=float(total_oldish / total_teams),
        collective_old=float(total_old / total_teams),
        age_std=2,
        girl_count=float(total_girls / total_teams),
    )

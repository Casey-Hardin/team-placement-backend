# native imports
from statistics import stdev

# external imports
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, TeamMetrics


def team_metrics(people: list[Person]) -> TeamMetrics:
    return TeamMetrics(
        size=len(people),
        age=stdev([x.age for x in people]),
        collectiveNew=len([x for x in people if x.collective == Collective.new]),
        collectiveNewish=len([x for x in people if x.collective == Collective.newish]),
        collectiveOldish=len([x for x in people if x.collective == Collective.oldish]),
        collectiveOld=len([x for x in people if x.collective == Collective.old]),
        male=len([x for x in people if x.gender == Gender.male]),
        female=len([x for x in people if x.gender == Gender.female]),
        firstTime=len([x for x in people if x.firstTime == BooleanEnum.yes]),
    )

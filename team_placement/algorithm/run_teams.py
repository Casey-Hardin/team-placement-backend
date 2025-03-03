# third-party imports
from fastapi import HTTPException

# external imports
from team_placement.algorithm.apply_controls import apply_controls
from team_placement.algorithm.assign_leaders import assign_leaders
from team_placement.algorithm.complete_teams import complete_teams
from team_placement.algorithm.define_targets import define_targets
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.third_pass import third_pass
from team_placement.algorithm.sift_cohorts import sift_cohorts
from team_placement.algorithm.prepare_people_for_teams import prepare_people_for_teams
from team_placement.algorithm.second_pass import second_pass
from team_placement.constants import PRIORITIES
from team_placement.schemas import (
    Collective,
    Control,
    Person,
    Team,
)
from team_placement.utils.helpers import find_new_people_complete, list_cohorts


def run_teams(
    all_people: list[Person], controls: list[Control], teams: list[Team]
) -> list[Person] | None:
    """
    Sorts people into teams.

    Parameters
    ----------
    people
        People to assign to teams.
    controls
        Controls by the user to guide people assignment.
    teams
        Teams for people assignment.

    Returns
    -------
    list[Person] | None
        People with teams assigned otherwise None.
    """
    # people and teams are needed
    if len(all_people) == 0 or len(teams) == 0:
        message = "Both people and teams are needed to place people on teams!"
        print(message)
        raise HTTPException(status_code=420, detail={"message": message})

    # prepare people for team placement
    people = prepare_people_for_teams(all_people)

    # define targets per team
    targets = define_targets(people, teams)

    print("assign leaders")

    # assign leaders to cohorts based on teams
    people = assign_leaders(people, teams)

    print("perform first pass")

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    people = first_pass(people)

    print("apply controls")

    people = apply_controls(people, controls)

    print("perform second pass")

    # assign new people with 0 or 1 preference to cohorts while
    # respecting demographic targets and cohorts forming teams
    # restart whenever someone is added to a cohort to capture new information
    people = second_pass(people, targets, len(teams))

    print("perform second pass must assign")

    # assign new people with 2+ preferences
    people = second_pass(people, targets, len(teams), must_assign=True)

    print("sift cohorts")

    # assign cohorts to cohorts with leaders having 0 or 1 possibilities
    # based on demographic targets
    people = sift_cohorts(people, targets, teams)

    print("perform third pass")

    # place the rest of preferred people for each new person
    people = third_pass(people, targets, teams, find_new_people_complete)

    print(len(list(set([x.cohort for x in people]))))

    # place people by preferences in order of priorities
    order = [
        Collective.new,
        Collective.newish,
        Collective.oldish,
        Collective.old,
    ]
    for category in order:
        print(len(list(set([x.cohort for x in people]))))
        people = third_pass(
            people,
            targets,
            teams,
            lambda group: [x for x in group if getattr(x, "collective") == category],
        )

    # final assigns to all teams
    people = complete_teams(people, targets, len(teams))

    print(list_cohorts(people))

    target_metrics = {priority: (getattr(targets, priority)) for priority in PRIORITIES}
    for k, v in target_metrics.items():
        print(f"{k}: {v}")
    print("-------------------------------------------------------")

    from team_placement.utils.helpers import collect_metrics, collect_representatives

    representatives = collect_representatives(people)
    for person in sorted(representatives, key=lambda x: x.team):
        print(person.team)
        metrics = {
            priority: (getattr(collect_metrics(people, person.cohort), priority))
            for priority in PRIORITIES
        }
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print(
            {
                priority: (getattr(collect_metrics(people, person.cohort), priority))
                for priority in PRIORITIES
            },
            person.team,
        )
        print("-------------------------------------------------------")

    print(list_cohorts(people))
    return None


if __name__ == "__main__":
    # native imports
    from pathlib import Path

    # third-party imports
    from fastapi import UploadFile
    import shortuuid

    # external imports
    from team_placement.utils.find_preferred_people import find_preferred_people
    from team_placement.utils.read_excel import read_excel
    from team_placement.schemas import BooleanEnum

    excel_path = Path(
        "C:/Users/ac56533/Desktop/dev/Team Placement/Responses - Altered.xlsx"
    )
    file = UploadFile(
        excel_path.open("rb"), size=excel_path.stat().st_size, filename=excel_path.name
    )
    all_people = read_excel(file)

    all_people = find_preferred_people([], all_people)

    team_names = list(set([x.team for x in all_people if x.leader == BooleanEnum.yes]))
    newTeams = [
        Team(index=shortuuid.ShortUUID().random(length=10), name=name)
        for name in team_names
    ]

    run_teams(all_people, [], newTeams)

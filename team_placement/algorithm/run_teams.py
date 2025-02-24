# third-party imports
from fastapi import HTTPException

# external imports
from team_placement.algorithm.apply_controls import apply_controls
from team_placement.algorithm.assign_leaders import assign_leaders
from team_placement.algorithm.complete_teams import complete_teams
from team_placement.algorithm.define_targets import define_targets
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.fourth_pass import fourth_pass
from team_placement.algorithm.helpers import sift_cohorts
from team_placement.algorithm.prepare_people_for_teams import prepare_people_for_teams
from team_placement.algorithm.second_pass import second_pass
from team_placement.constants import PRIORITIES
from team_placement.schemas import (
    Collective,
    Control,
    Person,
    Team,
)


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

    # assign leaders to cohorts based on teams
    cohorts = assign_leaders(people, teams)

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    new_people = [
        x
        for x in people
        if x.first_time
        and len(x.preferred) != 0
        and all([friend not in x.cohort.people for friend in x.preferred])
    ]
    new_people_left, cohorts = first_pass(new_people, cohorts)

    new_people_left, cohorts = apply_controls(
        new_people_left, people, cohorts, controls
    )

    # assign new people with 0 or 1 preference to cohorts while
    # respecting demographic targets and cohorts forming teams
    # restart whenever someone is added to a cohort to capture new information
    new_people_left, cohorts = second_pass(
        new_people_left, cohorts, targets, len(teams)
    )

    # assign new people with 2+ preferences
    _, cohorts = second_pass(
        new_people_left, cohorts, targets, len(teams), must_assign=True
    )

    print([cohort.to_list() for cohort in cohorts])
    return None

    # assign cohorts to cohorts with leaders having 0 or 1 possibilities
    # based on demographic targets
    cohorts = sift_cohorts(targets, cohorts)

    # place the rest of preferred people for each new person
    new_people = [
        person
        for person in people
        if person.first_time
        and len(
            [
                x.cohort
                for x in person.preferred
                if x not in person.cohort.people
                and (person.cohort.team == "" or x.cohort.team == "")
                and x not in person.cohort.banned_people
                and person.cohort.validate(targets, cohorts, x.cohort)
            ]
        )
        != 0
    ]
    previous_cohorts = [cohort.to_list() for cohort in cohorts]
    cohorts = fourth_pass(new_people, cohorts, targets, previous_cohorts)

    # place people by preferences in order of priorities
    order = [
        Collective.new,
        Collective.newish,
        Collective.oldish,
        Collective.old,
    ]
    for category in order:
        found_people = [x for x in people if getattr(x, "collective") == category]
        previous_cohorts = [cohort.to_list() for cohort in cohorts]
        cohorts = fourth_pass(found_people, cohorts, targets, previous_cohorts)

    # final assigns to all teams
    cohorts = complete_teams(cohorts, targets)

    target_metrics = {priority: (getattr(targets, priority)) for priority in PRIORITIES}
    for k, v in target_metrics.items():
        print(f"{k}: {v}")
    print("-------------------------------------------------------")
    for cohort in sorted(cohorts, key=lambda x: x.team):
        print(cohort.team)
        metrics = {priority: (getattr(cohort, priority)) for priority in PRIORITIES}
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print(
            {priority: (getattr(cohort, priority)) for priority in PRIORITIES},
            cohort.team,
        )
        print("-------------------------------------------------------")

    for cohort in sorted(cohorts, key=lambda x: x.team):
        print(cohort.to_list(), cohort.team)

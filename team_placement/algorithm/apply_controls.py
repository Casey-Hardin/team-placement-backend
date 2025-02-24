# external imports
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.objects import Cohort, PersonObject
from team_placement.schemas import Control


def apply_controls(
    new_people_left: list[PersonObject],
    people: list[PersonObject],
    cohorts: list[Cohort],
    controls: list[Control],
) -> tuple[list[PersonObject], list[Cohort]]:
    """
    Applies user controls to people and cohorts.

    Parameters
    ----------
    new_people_left
        New people still to assign.
    people
        All people to assign to teams.
    cohorts
        Functional groups of people in creating teams.
    controls
        Include / Exclude controls when placing people on teams.

    Returns
    -------
    list[PersonObject]
        New people still to be assigned.
    list[Cohort]
        Functional groups of people in creating teams where user controls are assigned.
    """
    # enforce user preferences
    for control in controls:
        person_1 = next(
            iter([x for x in people if x.index == control.personIndex]), None
        )
        if person_1 is None:
            continue

        # combine cohorts
        for person_index in control.teamInclude:
            # person_2 is missing
            person_2 = next(iter([x for x in people if x.index == person_index]), None)
            if person_2 is None:
                continue

            # leaders from different teams cannot be united
            # leader separation is assumed
            if person_1.cohort.team != "" and person_2.cohort.team != "":
                continue

            # cannot unite if the union is not blessed
            if (
                person_1 in person_2.cohort.banned_people
                or person_2 in person_1.cohort.banned_people
            ):
                continue

            # combine person_1 and person_2's cohorts
            cohorts = person_1.cohort.add(person_2.cohort, cohorts)

            # recurse
            new_people_left = [
                x
                for x in new_people_left
                if all([friend not in x.cohort.people for friend in x.preferred_people])
            ]
            new_people_left, cohorts = first_pass(new_people_left, cohorts)

        # separate cohorts
        for person_index in control.teamExclude:
            # person_2 is missing
            person_2 = next(iter([x for x in people if x.index == person_index]), None)
            if person_2 is None:
                continue

            # ignore people already united
            if person_1.cohort != person_2.cohort:
                person_1.cohort.banned_people.append(person_2)
                person_2.cohort.banned_people.append(person_1)
            new_people_left, cohorts = first_pass(new_people_left, cohorts)
    return new_people_left, cohorts

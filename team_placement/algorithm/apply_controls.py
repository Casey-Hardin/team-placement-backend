# external imports
from team_placement.algorithm.first_pass import first_pass
from team_placement.schemas import Control, Person
from team_placement.utils.helpers import join_cohorts


def apply_controls(
    people: list[Person],
    controls: list[Control],
) -> list[Person]:
    """
    Applies user controls to people and cohorts.

    Parameters
    ----------
    people
        All people to assign to teams.
    controls
        Include / Exclude controls when placing people on teams.

    Returns
    -------
    list[Person]
        People with controls assigned when creating teams.
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
            if person_1.team != "" and person_2.team != "":
                continue

            # cannot unite if the union is not blessed
            if person_1 in person_2.banned_people or person_2 in person_1.banned_people:
                continue

            # combine cohorts
            people = join_cohorts(person_1.cohort, person_2.cohort, people)

            # recurse
            people = first_pass(people)

        # separate cohorts
        for person_index in control.teamExclude:
            # person_2 is missing
            person_2 = next(iter([x for x in people if x.index == person_index]), None)
            if person_2 is None:
                continue

            # ignore people already united
            if person_1.cohort == person_2.cohort:
                continue

            # separate cohorts
            cohort_1 = [x for x in people if x.cohort == person_1.cohort]
            for person in cohort_1:
                person.banned_people.append(person_2.index)
            cohort_2 = [x for x in people if x.cohort == person_2.cohort]
            for person in cohort_2:
                person.banned_people.append(person_1.index)

            # recurse
            people = first_pass(people)
    return people

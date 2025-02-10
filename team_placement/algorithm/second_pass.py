# external imports
from team_placement.schemas import Targets
from team_placement.algorithm.objects import Cohort, PersonObject
from team_placement.algorithm.first_pass import first_pass
from team_placement.algorithm.helpers import prioritized_cohort


def second_pass(
    people: list[PersonObject],
    cohorts: list[Cohort],
    targets: Targets,
    must_assign: bool = False,
) -> tuple[list[PersonObject], list[Cohort]]:
    for person in people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        # check for validity based on targets + adding to other cohorts
        friend_cohorts = list(
            set(
                [
                    x.cohort
                    for x in person.preferred
                    if x not in person.cohort.people
                    and (person.cohort.team == "" or x.cohort.team == "")
                    and x not in person.cohort.banned_people
                ]
            )
        )

        strict_friend_cohorts = [
            x for x in friend_cohorts if person.cohort.validate(targets, cohorts, x)
        ]

        # take action when a new person has 0 or 1 possible preference
        leader_cohorts = [x for x in cohorts if x.team != ""]
        match len(strict_friend_cohorts):
            case 0:
                # adding person to a cohort with any of their friends
                # will exceed targets
                friend_cohort = prioritized_cohort(
                    person.cohort, friend_cohorts, targets, leader_cohorts
                )
            case 1:
                # this is the person's choice
                friend_cohort = strict_friend_cohorts[0]
            case _:
                # 2+ people are reasonable additions
                # too many choices at this time
                if not must_assign:
                    continue
                friend_cohort = prioritized_cohort(
                    person.cohort, strict_friend_cohorts, targets, leader_cohorts
                )

        # combine person and their friend's cohorts
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # recurse
        people = [x for x in people if x != person]
        people, cohorts = first_pass(people, cohorts)
        people, cohorts = second_pass(people, cohorts, targets)
        if must_assign:
            people, cohorts = second_pass(
                people, cohorts, targets, must_assign=must_assign
            )
        return people, cohorts
    return people, cohorts

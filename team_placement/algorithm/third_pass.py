# external imports
from . import schemas
from team_placement.algorithm.objects import Cohort, Person
from team_placement.algorithm.helpers import prioritized_cohort, sift_cohorts


def third_pass(
    people: list[Person],
    cohorts: list[Cohort],
    targets: schemas.Targets,
) -> list[Cohort]:
    current_people = list(people)
    for person in current_people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        # check for validity based on targets + adding to other cohorts
        strict_friend_cohorts = list(
            set(
                [
                    x.cohort
                    for x in person.preferred_people
                    if x not in person.cohort.people
                    and (
                        person.cohort.team_number is None
                        or x.cohort.team_number is None
                    )
                    and x not in person.cohort.user_banned_list
                    and person.cohort.validate(targets, cohorts, x.cohort)
                ]
            )
        )

        # take action when a new person has 0 or 1 possible preference
        match len(strict_friend_cohorts):
            case 0:
                # adding person to a cohort with any of their friends
                # will exceed targets
                people = [x for x in people if x != person]
                continue
            case 1:
                # this is the person's choice
                friend_cohort = strict_friend_cohorts[0]
            case _:
                # 2+ people are reasonable additions
                # assign the best choice for the cohort
                leader_cohorts = [x for x in cohorts if x.team_number is not None]
                friend_cohort = prioritized_cohort(
                    person.cohort,
                    strict_friend_cohorts,
                    targets,
                    leader_cohorts,
                    must_pick=False,
                )

                # validate is conservative
                # and doesn't take other cohorts into account
                if friend_cohort is None:
                    people = [x for x in people if x != person]
                    continue

        # combine person and their friend's cohorts
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # place cohorts with 0 or 1 possible to leader cohorts
        cohorts = sift_cohorts(targets, cohorts)

        # recurse
        people = [x for x in people if x != person]
    return cohorts

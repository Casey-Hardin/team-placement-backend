from team_placement.algorithm.objects import Cohort, Person


def first_pass(
    people: list[Person], cohorts: list[Cohort]
) -> tuple[list[Person], list[Cohort]]:
    current_people = list(people)
    for person in current_people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        friend_cohorts = list(
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
                ]
            )
        )

        # take action when a new person has 0 or 1 possible preference
        match len(friend_cohorts):
            case 0:
                # no new friends to add
                # remove the person from the list
                people = [x for x in people if x != person]
                continue
            case 1:
                # this is the person's choice
                friend_cohort = friend_cohorts[0]
            case _:
                # too many choices at this time
                continue

        # combine person and their friend's cohorts
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # recurse
        people = [x for x in people if x != person]
        return first_pass(people, cohorts)
    return people, cohorts

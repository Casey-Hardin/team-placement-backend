# native imports
from operator import attrgetter

# external imports
from team_placement.schemas import Person, Targets
from team_placement.constants import PRIORITIES
from team_placement.utils.helpers import (
    collect_metrics,
    copy_people,
    find_friends,
    join_cohorts,
)


def prioritized_friend(
    person: Person,
    possible_friends: list[Person],
    people: list[Person],
    targets: Targets,
    team_count: int,
    must_pick: bool = True,
) -> Person | None:
    """
    Finds the best friend for a person based on possible friends while meeting targets.

    Parameters
    ----------
    person
        A person.
    possible_friends
        Possible friends to be on a team with a person.
    people
        All people to assign to teams.
    targets
        Targets for each cohort.
    team_count
        Number of teams to assign people to.
    must_pick
        Flag to force assignment of people to cohorts.

    Returns
    -------
    Person | None
        Friend to join with the prospective cohort.
    """
    # friends cannot be the prospective cohort
    # one or both cohorts must not have a team
    # the union cannot be banned
    # friends do not have to be preferred by the person
    friends = find_friends(person, people, possible_friends, False)

    # collect metrics from each prospective union
    pretend_metrics_dict: dict[str, Targets] = {}
    for friend in friends:
        # combine people and banned lists
        pretend_people = copy_people(people)
        pretend_people = join_cohorts(person.cohort, friend.cohort, pretend_people)

        # values on each target after joining cohorts
        pretend_metrics_dict[friend.index] = collect_metrics(
            pretend_people, person.cohort
        )

    # no friends form a valid pair
    if len(pretend_metrics_dict) == 0:
        return None

    # filter cohorts based on target priorities
    indices = [x.index for x in friends]
    max_values = {}
    tolerance = 1
    leader_cohorts = list(set([x.cohort for x in people if x.team != ""]))
    for priority in PRIORITIES:
        # minimum value to meet targets
        min_allowed = getattr(targets, priority) - tolerance
        min_allowed = min_allowed if min_allowed > 0 else 0

        # find the maximum allowed value for each target
        if priority == "age_std":
            # age is based on standard deviation rather than count
            max_value = getattr(targets, priority) + tolerance
        else:
            # max value is calculated prior to joining cohorts
            # priority is based on count
            # account for the number of people left to assign
            # for example 99 of 100 people are assigned, so 1 person is left
            # a team may have 7 people and the target is 9
            # 8 is the max as there is only one more person to assign
            number_assigned = (
                sum(
                    [
                        getattr(collect_metrics(people, x), priority)
                        for x in leader_cohorts
                    ]
                )
                - min_allowed * team_count
            )
            number_left = (
                getattr(targets, priority) * team_count
                - number_assigned
                - min_allowed * team_count
            )
            max_value = min(
                getattr(collect_metrics(people, person.cohort), priority) + number_left,
                getattr(targets, priority) + tolerance,
            )

        # minimum value must be maintained
        max_value = max_value if max_value > min_allowed else min_allowed
        max_values[priority] = max_value

        # filter out cohorts that exceed the maximum value
        for index, fake_metrics in pretend_metrics_dict.items():
            # metric exceeds the maximum allowed value
            above_max = getattr(fake_metrics, priority) > max_value

            # smallest value of possible cohorts based on a metric
            filtered_metrics = [
                v for k, v in pretend_metrics_dict.items() if k in indices
            ]
            min_value = getattr(
                min(filtered_metrics, key=attrgetter(priority)), priority
            )

            # remove possible cohorts that aren't the best match
            if above_max and getattr(fake_metrics, priority) != min_value:
                indices = [x for x in indices if x != index]

    # pick a breaking choice when required
    filtered_metrics = [v for k, v in pretend_metrics_dict.items() if k in indices]
    if not must_pick and all(
        [
            any(
                [getattr(x, priority) > max_values[priority] for priority in PRIORITIES]
            )
            for x in filtered_metrics
        ]
    ):
        return None

    # either must assign is set or there are valid cohorts
    # filter cohorts based on target priorities
    for priority in PRIORITIES:
        for index, fake_metrics in pretend_metrics_dict.items():
            valid = getattr(fake_metrics, priority) <= getattr(targets, priority)

            filtered_metrics = [
                v for k, v in pretend_metrics_dict.items() if k in indices
            ]
            min_value = getattr(
                min(filtered_metrics, key=attrgetter(priority)), priority
            )
            if not valid and getattr(fake_metrics, priority) != min_value:
                indices = [x for x in indices if x != index]

    # filter cohorts based on demographic priorities
    for priority in PRIORITIES:
        filtered_metrics = [v for k, v in pretend_metrics_dict.items() if k in indices]
        min_value = getattr(min(filtered_metrics, key=attrgetter(priority)), priority)
        indices = [
            x
            for x in indices
            if getattr(pretend_metrics_dict[x], priority) == min_value
        ]
    return next(iter([x for x in friends if x.index == indices[0]]), None)

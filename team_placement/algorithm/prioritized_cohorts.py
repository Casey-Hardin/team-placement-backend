# native imports
from copy import deepcopy
from operator import attrgetter

# external imports
from team_placement import schemas
from team_placement.constants import PRIORITIES
from team_placement.algorithm.objects import Cohort


def prioritized_cohort(
    prospective_cohort: Cohort,
    friend_cohorts: list[Cohort],
    targets: schemas.Targets,
    leader_cohorts: list[Cohort],
    must_pick: bool = True,
) -> Cohort | None:
    """
    Finds the best cohort for a person based on possible friend cohorts.

    Parameters
    ----------
    prospective_cohort
        Cohort to join with a friend cohort.
    friend_cohorts
        Possible cohorts to combine with the prospective cohort.
    targets
        Targets for each cohort.
    leader_cohorts
        Cohorts with leaders.
    must_pick
        Flag to force assignment of people to cohorts.

    Returns
    -------
    Cohort | None
        Friend cohort to join with the prospective cohort.
    """
    # friend cohorts cannot be the prospective cohort
    # one or both cohorts must not have a team
    # the union cannot be banned
    allowed_cohorts = [
        x
        for x in friend_cohorts
        if x != prospective_cohort
        and (x.team == "" or prospective_cohort.team == "")
        and all([friend not in prospective_cohort.banned_people for friend in x.people])
    ]

    # no friend cohorts form a valid pair
    if len(allowed_cohorts) == 0:
        return None

    # collect metrics from each prospective union
    pretend_metrics = []
    for cohort in allowed_cohorts:
        # combine people and banned lists
        people = deepcopy(prospective_cohort.people + cohort.people)
        banned_list = deepcopy(
            prospective_cohort.banned_people
            + [
                x
                for x in cohort.banned_people
                if x not in prospective_cohort.banned_people
            ]
        )

        # working cohort to test
        pretend_cohort = Cohort(people)
        pretend_cohort.banned_people = banned_list

        # values on each target after joining cohorts
        pretend_metrics.append(pretend_cohort.metrics())
    pretend_indices = {index: metrics for index, metrics in enumerate(pretend_metrics)}

    # filter cohorts based on target priorities
    filtered_metrics = list(pretend_metrics)
    tolerance = 1
    max_values = {}
    for priority in PRIORITIES:
        # minimum value to meet targets
        min_allowed = getattr(targets, priority) - tolerance
        min_allowed = min_allowed if min_allowed > 0 else 0

        # find the maximum allowed value for each target
        if priority == "age_std":
            # age is based on standard deviation rather than count
            max_value = getattr(targets, priority) + tolerance
        else:
            # priority is based on count
            # account for the number of people left to assign
            # for example 99 of 100 people are assigned, so 1 person is left
            # a team may have 7 people and the target is 9
            # 8 is the max as there is only one more person to assign
            number_assigned = sum(
                [getattr(x, priority) for x in leader_cohorts]
            ) - min_allowed * len(leader_cohorts)
            number_left = (
                getattr(targets, priority) * len(leader_cohorts)
                - number_assigned
                - min_allowed * len(leader_cohorts)
            )
            max_value = min(
                getattr(prospective_cohort, priority) + number_left,
                getattr(targets, priority) + tolerance,
            )

        # minimum value must be maintained
        max_value = max_value if max_value > min_allowed else min_allowed
        max_values[priority] = max_value

        # filter out cohorts that exceed the maximum value
        for fake_metrics in pretend_metrics:
            # metric exceeds the maximum allowed value
            above_max = getattr(fake_metrics, priority) > max_value

            # smallest value of possible cohorts based on a metric
            min_value = getattr(
                min(filtered_metrics, key=attrgetter(priority)), priority
            )

            # remove possible cohorts that aren't the best match
            if above_max and getattr(fake_metrics, priority) != min_value:
                filtered_metrics = [x for x in filtered_metrics if x != fake_metrics]

    # pick a breaking choice when required
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
        for fake_metrics in pretend_metrics:
            valid = getattr(fake_metrics, priority) <= getattr(targets, priority)
            min_value = getattr(
                min(filtered_metrics, key=attrgetter(priority)), priority
            )
            if not valid and getattr(fake_metrics, priority) != min_value:
                filtered_metrics = [x for x in filtered_metrics if x != fake_metrics]

    # filter cohorts based on demographic priorities
    for priority in PRIORITIES:
        min_value = getattr(min(filtered_metrics, key=attrgetter(priority)), priority)
        filtered_metrics = [
            x for x in filtered_metrics if getattr(x, priority) == min_value
        ]
    index = [
        key for key, value in pretend_indices.items() if value == filtered_metrics[0]
    ][0]
    return allowed_cohorts[index]

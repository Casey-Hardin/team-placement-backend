# native imports
from operator import attrgetter

# external imports
from team_placement import schemas
from team_placement.constants import PRIORITIES
from team_placement.algorithm.objects import Cohort


def sift_cohorts(
    targets: schemas.Targets,
    cohorts: list[Cohort],
) -> list[Cohort]:
    previous_cohorts = [x.to_list() for x in cohorts]
    for cohort in cohorts:
        if cohort.team != "":
            continue

        leader_cohorts = [x for x in cohorts if x.team != ""]
        valid_leader_cohorts = [
            x for x in leader_cohorts if cohort.validate(targets, cohorts, x)
        ]
        match len(valid_leader_cohorts):
            case 0:
                leader_cohort = prioritized_cohort(
                    cohort, leader_cohorts, targets, leader_cohorts
                )
            case 1:
                leader_cohort = valid_leader_cohorts[0]
            case _:
                # too many choices at this time
                continue

        # combine person and their friend's cohorts
        cohorts = leader_cohort.add(cohort, cohorts)
    if previous_cohorts != [x.to_list() for x in cohorts]:
        return sift_cohorts(targets, cohorts)
    return cohorts


def prioritized_cohort(
    prospective_cohort: Cohort,
    friend_cohorts: list[Cohort],
    targets: schemas.Targets,
    leader_cohorts: list[Cohort],
    must_pick: bool = True,
) -> Cohort | None:
    allowed_cohorts = [
        x
        for x in friend_cohorts
        if x != prospective_cohort
        and (x.team == "" or prospective_cohort.team == "")
        and all([friend not in prospective_cohort.banned_people for friend in x.people])
    ]
    if len(allowed_cohorts) == 0:
        return None

    pretend_metrics = []
    for cohort in allowed_cohorts:
        fake_metrics = schemas.Targets(
            **{
                priority: (
                    getattr(prospective_cohort, priority) + getattr(cohort, priority)
                )
                for priority in PRIORITIES
            }
        )
        pretend_metrics.append(fake_metrics)
    pretend_indices = {index: metrics for index, metrics in enumerate(pretend_metrics)}

    filtered_metrics = list(pretend_metrics)
    tolerance = 1
    max_values = {}
    for priority in PRIORITIES:
        min_allowed = getattr(targets, priority) - tolerance
        min_allowed = min_allowed if min_allowed > 0 else 0
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
        max_value = max_value if max_value > min_allowed else min_allowed
        max_values[priority] = max_value
        for fake_metrics in pretend_metrics:
            above_max = getattr(fake_metrics, priority) > max_value
            min_value = getattr(
                min(filtered_metrics, key=attrgetter(priority)), priority
            )
            if above_max and getattr(fake_metrics, priority) != min_value:
                filtered_metrics = [x for x in filtered_metrics if x != fake_metrics]

    # don't pick a breaking choice if you don't have to
    if not must_pick and all(
        [
            any(
                [getattr(x, priority) > max_values[priority] for priority in PRIORITIES]
            )
            for x in filtered_metrics
        ]
    ):
        return None

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

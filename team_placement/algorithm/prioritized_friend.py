# native imports
from statistics import stdev

# external imports
from team_placement.schemas import Collective, Gender, Person, Targets
from team_placement.constants import PRIORITIES
from team_placement.utils.helpers import (
    collect_metrics,
    find_friends,
)


def find_other_people(
    people_in_cohort: list[Person], people: list[Person]
) -> list[Person]:
    """
    Collects people who could potentially cohort with people in cohort.

    Parameters
    ----------
    people_in_cohort
        People in a cohort.
    people
        All people to assign to teams.

    Returns
    -------
    list[Person]
        People who could potentially cohort with people already in cohort.
    """
    all_friends = [find_friends(x, people, None, False, True) for x in people_in_cohort]
    return [x for x in people if all([x in y for y in all_friends])]


def age_offset(
    people_in_cohort: list[Person],
    people: list[Person],
    team_size: int,
    target_age_std: float,
) -> int:
    """
    Finds the number of people to add to a cohort to meet the target age standard deviation.
    People added to the cohort are the worst match for the cohort based on age.

    Parameters
    ----------
    people_in_cohort
        People in a cohort. Representatives only is okay.
    people
        All people to assign to teams.
    team_size
        Number of people to add to a team.
    target_age_std
        Target age standard deviation.

    Returns
    -------
    int
        Number of people to add to a cohort to meet the target age standard deviation.
    """
    # collect ages of people in cohort
    ages = [x.age for x in people if x.cohort in [y.cohort for y in people_in_cohort]]

    # collect ages of people who could potentially cohort with people in cohort
    other_people = find_other_people(people_in_cohort, people)
    other_ages = [x.age for x in other_people]

    # find the number of worst matches based on age to add to cohort to meet target
    for count in range(team_size):
        # no more people to add to cohort
        # the limit does not exist
        if len(other_ages) == 0:
            return team_size

        # calculate the standard deviation of ages based on a full team size
        # add the mean age as best case scenario
        mean_age = sum(ages) / len(ages)
        new_ages = ages + [mean_age] * (team_size - len(ages))
        age_std = stdev(new_ages)

        # target age standard deviation is met
        if age_std > target_age_std:
            # print(new_ages)
            return count

        # add the worst match based on age to the cohort
        worst_age = max(other_ages, key=lambda x: abs(x - mean_age))
        ages = ages + [worst_age]
        other_ages.remove(worst_age)
    return team_size


def collect_offsets(
    person: Person,
    friend: Person,
    people: list[Person],
    targets: Targets,
    team_count: int,
) -> Targets:
    """
    Collects the number of people to add to a cohort to meet the target values.

    Parameters
    ----------
    person
        A person.
    friend
        A friend of the person.
    people
        All people to assign to teams.
    targets
        Targets for each cohort.
    team_count
        Number of teams for team placement.

    Returns
    -------
    Targets
        Number of people to add to a cohort to meet the target values.
    """
    friend_metrics = collect_metrics(people, [person.cohort, friend.cohort])
    other_people = find_other_people([person, friend], people)

    # calculate the maximum number of people to add on each priority
    # based on people left to be assigned
    max_values = {}
    tolerance = 1
    leader_cohorts = list(set([x.cohort for x in people if x.team != ""]))
    for priority in PRIORITIES:
        # minimum value to meet targets
        min_allowed = getattr(targets, priority) - tolerance
        min_allowed = min_allowed if min_allowed > 0 else 0

        # max value is calculated prior to joining cohorts
        # priority is based on count
        # account for the number of people left to assign
        # for example 99 of 100 people are assigned, so 1 person is left
        # a team may have 7 people and the target is 9
        # 8 is the max as there is only one more person to assign
        number_assigned = (
            sum([getattr(collect_metrics(people, x), priority) for x in leader_cohorts])
            - min_allowed * team_count
        )
        number_left = (
            getattr(targets, priority) * team_count
            - number_assigned
            - min_allowed * team_count
        )
        max_value = min(
            getattr(collect_metrics(people, person.cohort), priority) + number_left,
            getattr(targets, priority),
        )

        # minimum value must be maintained
        max_value = max_value if max_value > min_allowed else min_allowed
        max_values[priority] = max_value

    team_size_offset = max_values["team_size"] - friend_metrics.team_size
    if team_size_offset > len(other_people):
        team_size_offset = targets.team_size

    new_offset = max_values["collective_new"] - friend_metrics.collective_new
    if new_offset > len([x for x in other_people if x.collective == Collective.new]):
        new_offset = targets.team_size

    newish_offset = max_values["collective_newish"] - friend_metrics.collective_newish
    if newish_offset > len(
        [x for x in other_people if x.collective == Collective.newish]
    ):
        newish_offset = targets.team_size

    oldish_offset = max_values["collective_oldish"] - friend_metrics.collective_oldish
    if oldish_offset > len(
        [x for x in other_people if x.collective == Collective.oldish]
    ):
        oldish_offset = targets.team_size

    old_offset = max_values["collective_old"] - friend_metrics.collective_old
    if old_offset > len([x for x in other_people if x.collective == Collective.old]):
        old_offset = targets.team_size

    girl_offset = max_values["girl_count"] - friend_metrics.girl_count
    if girl_offset > len([x for x in other_people if x.gender == Gender.female]):
        girl_offset = targets.team_size

    return Targets(
        team_size=team_size_offset,
        collective_new=new_offset,
        collective_newish=newish_offset,
        collective_oldish=oldish_offset,
        collective_old=old_offset,
        age_std=age_offset(
            [person, friend], people, int(targets.team_size), targets.age_std
        ),
        girl_count=girl_offset,
    )


def prioritized_friend(
    person: Person,
    possible_friends: list[Person],
    people: list[Person],
    targets: Targets,
    team_count: int,
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
        Number of teams for team placement.

    Returns
    -------
    Person | None
        Friend to join with the prospective cohort.
    """
    # sanitize friends
    # friends cannot be the prospective cohort
    # one or both cohorts must not have a team
    # the union cannot be banned
    # friends do not have to be preferred by the person
    friends = find_friends(person, people, possible_friends, False)

    if person.firstName == "None":
        print([str(x) for x in friends])

    # collect metrics from each prospective union
    offsets_dict: dict[str, Targets] = {}
    for friend in friends:
        offsets_dict[friend.index] = collect_offsets(
            person, friend, people, targets, team_count
        )

    if person.firstName == "None":
        print(offsets_dict)
        assert False

    # no friends form a valid pair
    if len(offsets_dict) == 0:
        return None

    # find the friend having the maximum offset from target values
    selected_friend = friends[0]
    for friend in friends[1:]:
        # find priorities where friends are not equal
        local_priorities = [
            priority
            for priority in PRIORITIES
            if not all(
                [
                    getattr(offsets_dict[x.index], priority)
                    == getattr(offsets_dict[selected_friend.index], priority)
                    for x in [selected_friend, friend]
                ]
            )
        ]

        # no priorities are different
        if len(local_priorities) == 0:
            continue

        # find the flexibility for each friend to have additional people added to their cohort
        min_offset = min(
            [
                getattr(offsets_dict[selected_friend.index], priority)
                for priority in local_priorities
            ]
        )

        friend_min_offset = min(
            [
                getattr(offsets_dict[friend.index], priority)
                for priority in local_priorities
            ]
        )

        # current friend is flexible
        if min_offset > friend_min_offset:
            continue

        # new friend is more flexible
        if friend_min_offset > min_offset:
            selected_friend = friend
            continue

        # runoff based on demographic priorities
        for priority in PRIORITIES:
            if getattr(offsets_dict[selected_friend.index], priority) == min_offset:
                # current friend is flexible
                break
            elif getattr(offsets_dict[friend.index], priority) == min_offset:
                # new friend is more flexible
                selected_friend = friend
                break
    return selected_friend

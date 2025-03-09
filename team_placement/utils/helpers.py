# native imports
from statistics import stdev

# external imports
from team_placement.constants import PRIORITIES
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, Targets


def adjusted_stdev(ages: list[int], team_size: int) -> float:
    """
    Adjusts the standard deviation of ages for a team size.

    Parameters
    ----------
    ages
        Ages of people on a team.
    team_size
        Number of people on a team.

    Returns
    -------
    float
        Adjusted standard deviation of ages for a team size.
    """
    mean_age = sum(ages) / len(ages)
    new_ages = ages + [mean_age] * (int(team_size) - len(ages))
    return stdev(new_ages)


def collect_metrics(
    people: list[Person],
    cohorts: str | list[str],
    adjust_age: bool = False,
    target_team_size: int | None = None,
) -> Targets:
    """
    Collects metrics for a cohort based on people in the cohort.

    Parameters
    ----------
    people
        All people to place on teams.
    cohort
        Cohort(s) to collect metrics for.
    adjust_age
        Flag to adjust the standard deviation of ages for a team size.
    target_team_size
        Number of people on a team.

    Returns
    -------
    Targets
        Metrics for cohort(s).
    """
    if isinstance(cohorts, str):
        cohorts = [cohorts]

    people_in_cohort = [x for x in people if x.cohort in cohorts]

    team_size = len(people_in_cohort)
    ages = [x.age for x in people_in_cohort]

    # scale age standard deviation to a full team size
    age_std = stdev(ages) if len(ages) > 1 else 0
    if adjust_age and target_team_size is not None:
        age_std = adjusted_stdev(ages, target_team_size)

    collective_new = len(
        [x for x in people_in_cohort if x.collective == Collective.new]
    )
    collective_newish = len(
        [x for x in people_in_cohort if x.collective == Collective.newish]
    )
    collective_oldish = len(
        [x for x in people_in_cohort if x.collective == Collective.oldish]
    )
    collective_old = len(
        [x for x in people_in_cohort if x.collective == Collective.old]
    )
    girl_count = len([x for x in people_in_cohort if x.gender == Gender.female])

    return Targets(
        team_size=team_size,
        collective_new=collective_new,
        collective_newish=collective_newish,
        collective_oldish=collective_oldish,
        collective_old=collective_old,
        age_std=age_std,
        girl_count=girl_count,
    )


def collect_representatives(people: list[Person]) -> list[Person]:
    """
    Collects representative friends from each cohort within friends.

    Parameters
    ----------
    friends
        Friends to possibly cohort with a person.

    Returns
    -------
    list[Person]
        Representative friends from unique cohorts to possibly cohort with a person.
    """
    # find friend representatives
    friend_representatives: list[Person] = []
    for friend in people:
        if friend.cohort not in [x.cohort for x in friend_representatives]:
            friend_representatives.append(friend)
    return friend_representatives


def find_friends(
    person: Person,
    people: list[Person],
    possible_friends: list[Person] | None = None,
    preferred: bool = True,
    all_people: bool = False,
) -> list[Person]:
    """
    Finds friends for a person based on preferences.
    Leaders cannot cohort with leaders from other teams - only room together
    Does not consider person preferences rejected by user.

    Parameters
    ----------
    person
        A person.
    people
        All people to assign to teams.
    possible_friends
        Possible friends to be on a team with a person.
    preferred
        Flag to consider only people preferred by person.
    all_people
        Flag to consider all people or just representatives.

    Returns
    -------
    list[Person]
        Friends to possibly cohort with a person.
    """
    if possible_friends is None:
        possible_friends = people

    # find friends and their cohorts
    friends = [
        friend
        for friend in possible_friends
        if (person.team == "" or friend.team == "")
        and friend.cohort != person.cohort
        and (friend.index in person.preferredPeople or not preferred)
        and all(
            [
                x not in person.banned_people
                for x in [y.index for y in people if y.cohort == friend.cohort]
            ]
        )
    ]
    if all_people:
        return friends
    return collect_representatives(friends)


def find_friends_strict(
    person: Person,
    possible_friends: list[Person],
    people: list[Person],
    targets: Targets,
    team_count: int,
) -> list[Person]:
    """
    Finds possible friends and their cohorts for a person based on targets.
    Age is skipped when screening due to the nature of calculating standard deviation.

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
        Number of teams to create.

    Returns
    -------
    list[Person]
        Possible friends for a person that will meet targets when cohorting.
    """
    # friends cannot already cohort with the person
    possible_friends = [x for x in possible_friends if x.cohort != person.cohort]
    friends = collect_representatives(possible_friends)

    # collect leaders of teams in use
    leaders = collect_representatives([x for x in people if x.team != ""])

    # check for validity based on targets and adding to leader cohorts
    friends_strict: list[Person] = []
    for friend in friends:
        metrics = collect_metrics(
            people,
            [person.cohort, friend.cohort],
            adjust_age=True,
            target_team_size=targets.team_size,
        )

        # team must meet targets
        if person.team != "" or friend.team != "" or len(leaders) != team_count:
            if all(
                [
                    getattr(metrics, priority) <= getattr(targets, priority)
                    for priority in PRIORITIES
                ]
            ):
                friends_strict.append(friend)
            continue

        # cohort must add to a team while meeting targets
        people_in_cohort = [
            x for x in people if x.cohort in [person.cohort, friend.cohort]
        ]
        for leader in leaders:
            if any([x.index in leader.banned_people for x in people_in_cohort]):
                continue

            # friend is valid if a leader cohort can be joined
            metrics = collect_metrics(
                people,
                [person.cohort, friend.cohort, leader.cohort],
                adjust_age=True,
                target_team_size=targets.team_size,
            )

            if all(
                [
                    getattr(metrics, priority) <= getattr(targets, priority)
                    for priority in PRIORITIES
                ]
            ):
                friends_strict.append(friend)
                break
    return friends_strict


def find_new_people(people: list[Person]) -> list[Person]:
    """
    Collects indices to first time people from a list of people.
    They are not yet paired with any of their preferences.

    Parameters
    ----------
    people
        All people to place on teams.

    Returns
    -------
    list[Person]
        People who are not matched with any of their preferences.
    """
    new_people = [
        x
        for x in people
        if x.firstTime == BooleanEnum.yes
        and len(x.preferredPeople) != 0
        and all(
            [
                index not in [y.index for y in people if y.cohort == x.cohort]
                for index in x.preferredPeople
            ]
        )
    ]
    new_people.sort(key=lambda x: x.order)
    return new_people


def find_new_people_complete(people: list[Person]) -> list[Person]:
    """
    Collects new people with unmet preferences that meet targets.

    Parameters
    ----------
    people
        All people to place on teams.

    Returns
    -------
    list[Person]
        New people with further preferences to meet.
    """
    new_people = [
        x
        for x in people
        if x.firstTime == BooleanEnum.yes
        and len(x.preferredPeople) != 0
        and any(
            [
                index not in [y.index for y in people if y.cohort == x.cohort]
                and index not in x.banned_people
                for index in x.preferredPeople
            ]
        )
    ]
    new_people.sort(key=lambda x: x.order)
    return new_people


def join_cohorts(cohort_1: str, cohort_2: str, people: list[Person]) -> list[Person]:
    """
    Joins cohorts.
    The identifier for the first cohort is adopted.

    Parameters
    ----------
    cohort_1
        A cohort.
    cohort_2
        A second cohort.
    people
        All people to place on teams.

    Returns
    -------
    list[Person]
        People with updated cohorts.
    """
    # find existing people in cohort
    people_to_update = [x for x in people if x.cohort in [cohort_1, cohort_2]]

    # collect banned people
    team = next(iter([x.team for x in people_to_update if x.team != ""]), "")
    banned_people = list(
        set([index for x in people_to_update for index in x.banned_people])
    )

    # update people
    for person_to_update in people_to_update:
        person_to_update.cohort = cohort_1
        person_to_update.team = team
        person_to_update.banned_people = banned_people

    # update banned people for all people effected by joining cohorts
    for person in people:
        if any([x.index in person.banned_people for x in people_to_update]):
            person.banned_people = list(
                set(person.banned_people + [x.index for x in people_to_update])
            )
    return people


def list_cohorts(people: list[Person]) -> list[list[str]]:
    """
    Full names of people who belong to cohorts.

    Returns
    -------
    list[str]
        Full names of people who belong to cohorts.
    """
    cohorts = [
        [x for x in people if x.cohort == cohort]
        for cohort in set([x.cohort for x in people])
    ]
    cohorts.sort(key=lambda x: min(x, key=lambda y: y.order).order)
    return [[str(person) for person in cohort] for cohort in cohorts]

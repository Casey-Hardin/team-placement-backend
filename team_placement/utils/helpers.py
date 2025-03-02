# native imports
from copy import deepcopy
from statistics import stdev

# external imports
from team_placement.constants import PRIORITIES
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, Targets


def collect_metrics(people: list[Person], cohort: str) -> Targets:
    """
    Collects metrics for a cohort based on people in the cohort.

    Parameters
    ----------
    people
        All people to place on teams.
    cohort
        Cohort to collect metrics for.

    Returns
    -------
    Targets
        Metrics for a cohort.
    """
    people_in_cohort = [x for x in people if x.cohort == cohort]

    team_size = len(people_in_cohort)
    ages = [x.age for x in people_in_cohort]
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
        age_std=stdev(ages) if len(ages) > 1 else 0,
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
    cohorts = list(set([x.cohort for x in people]))

    # find friend representatives
    friend_representatives = []
    for cohort in cohorts:
        friend = next(iter([x for x in people if x.cohort == cohort]), None)
        if friend is None:
            continue
        friend_representatives.append(friend)
    return friend_representatives


def find_friends(
    person: Person,
    people: list[Person],
    possible_friends: list[Person] | None = None,
    preferred: bool = True,
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
        and friend.index != person.index
        and (friend.index in person.preferredPeople or not preferred)
        and all(
            [
                x not in person.banned_people
                for x in [y.index for y in people if y.cohort == friend.cohort]
            ]
        )
    ]
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
    possible_friends = [x for x in possible_friends if x.index != person.index]
    friends = collect_representatives(possible_friends)

    # check for validity based on targets and adding to leader cohorts
    friends_strict: list[Person] = []
    for friend in friends:
        # cohorts must not be modified from searching for new friends
        pretend_people = deepcopy(people)

        # a pretend person and friend are not needed to join cohorts
        pretend_people = join_cohorts(person.cohort, friend.cohort, pretend_people)
        pretend_person = next(
            iter([x for x in pretend_people if x.index == person.index]), None
        )
        if pretend_person is None:
            continue

        # values on each target after joining cohorts
        pretend_metrics = collect_metrics(pretend_people, pretend_person.cohort)

        # collect cohorts of leaders - same as team names in use
        pretend_leader_cohorts = list(
            set([x.cohort for x in pretend_people if x.team != ""])
        )

        # team must meet targets
        # standard deviation is difficult to work with at low team sizes
        # best to ignore it when screening
        # it is applied when selecting the best of many options in a later step
        if pretend_person.team != "" or len(pretend_leader_cohorts) != team_count:
            if all(
                [
                    getattr(pretend_metrics, priority) <= getattr(targets, priority)
                    for priority in PRIORITIES
                    if priority != "age_std"
                ]
            ):
                friends_strict.append(friend)
            continue

        # cohort must add to a team while meeting targets
        for pretend_cohort in pretend_leader_cohorts:
            # start over for each leader cohort possibility
            new_pretend_people = deepcopy(pretend_people)

            # friend is valid if a leader cohort can be joined
            new_pretend_people = join_cohorts(
                pretend_person.cohort, pretend_cohort, new_pretend_people
            )
            new_pretend_metrics = collect_metrics(
                new_pretend_people, pretend_person.cohort
            )
            if all(
                [
                    getattr(new_pretend_metrics, priority) <= getattr(targets, priority)
                    for priority in PRIORITIES
                ]
            ):
                friends_strict.append(friend)
                break
    return friends_strict

    # may need to add back in later - test cases will have to decide
    other_cohorts = [x for x in cohorts if x != self and x != test_cohort]
    for priority in PRIORITIES:
        valid = getattr(pretend_metrics, priority) <= getattr(targets, priority)
        min_value = getattr(min(other_cohorts, key=attrgetter(priority)), priority)
        if valid:
            other_cohorts = [
                x
                for x in other_cohorts
                if getattr(x, priority)
                <= getattr(targets, priority) - getattr(self, priority)
            ]
        else:
            other_cohorts = [
                x for x in other_cohorts if getattr(x, priority) == min_value
            ]
        if not valid and getattr(test_cohort, priority) != min_value:
            return False
    return True


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
    return [
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


def find_new_people_complete(
    people: list[Person], targets: Targets, team_count: int
) -> list[str]:
    """
    Collects indices of new people who have unmet preferences that meet targets.

    Parameters
    ----------
    people
        All people to place on teams.
    targets
        Targets for each cohort to meet.
    team_count
        Number of teams to create.

    Returns
    -------
    list[str]
        Indices for new people who have further preferences to meet.
    """
    new_people = []
    for person in people:
        new_friends = [
            x
            for x in people
            if x.index in person.preferredPeople and x.cohort != person.cohort
        ]

        # find new friends based on targets
        _, new_cohorts = find_friends_strict(
            person, new_friends, people, targets, team_count
        )
        if len(new_cohorts) > 0:
            new_people.append(person)
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

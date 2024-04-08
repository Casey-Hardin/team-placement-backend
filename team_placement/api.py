# native imports
from operator import attrgetter
from typing import Annotated

# third-party imports
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# external imports
from . import schemas
from .constants import PRIORITIES
from .objects import Cohort, Person
from .read_excel import read_excel


# create a Fast API application
app = FastAPI()

# add middleware to communicate with ReactJS
origins = [
    "http://localhost:5173",
    "localhost:5173",
    ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def homepage() -> None:
    """ Homepage. """
    return {"message": "Hello World"}


def prioritized_cohort(
        prospective_cohort: Cohort,
        friend_cohorts: list[Cohort],
        targets: schemas.Targets,
    ) -> Cohort | None:
    allowed_cohorts = [
        x for x in friend_cohorts
        if x != prospective_cohort
            and (x.team_number is None
            or prospective_cohort.team_number is None)
            and all([friend not in prospective_cohort.user_banned_list
                for friend in x.people])
    ]
    if len(allowed_cohorts) == 0:
        return None

    pretend_metrics = []
    for cohort in allowed_cohorts:
        fake_metrics = schemas.Targets(
            **{priority: (
                getattr(prospective_cohort, priority)
                + getattr(cohort, priority)
            ) for priority in PRIORITIES}
        )
        pretend_metrics.append(fake_metrics)
    pretend_indices = {index: metrics for index, metrics in enumerate(pretend_metrics)}

    filtered_metrics = list(pretend_metrics)
    for priority in PRIORITIES:
        for fake_metrics in pretend_metrics:
            above_max = getattr(fake_metrics, priority) > getattr(targets, priority) + 2
            min_value = getattr(min(filtered_metrics, key=attrgetter(priority)), priority)
            if above_max and getattr(fake_metrics, priority) != min_value:
                filtered_metrics = [x for x in filtered_metrics if x != fake_metrics]

    for priority in PRIORITIES:
        for fake_metrics in pretend_metrics:
            valid = getattr(fake_metrics, priority) <= getattr(targets, priority)
            min_value = getattr(min(filtered_metrics, key=attrgetter(priority)), priority)
            if not valid and getattr(fake_metrics, priority) != min_value:
                filtered_metrics = [x for x in filtered_metrics if x != fake_metrics]

    # filter cohorts based on demographic priorities
    for priority in PRIORITIES:
        min_value = getattr(min(filtered_metrics, key=attrgetter(priority)), priority)
        filtered_metrics = [x for x in filtered_metrics if getattr(x, priority) == min_value]
    index = [key for key, value in pretend_indices.items() if value == filtered_metrics[0]][0]
    return allowed_cohorts[index]


def sift_cohorts(
        targets: schemas.Targets,
        cohorts: list[Cohort],
    ) -> list[Cohort]:
    for cohort in cohorts:
        if cohort.team_number != None:
            continue

        leader_cohorts = [x for x in cohorts if x.team_number is not None]
        valid_leader_cohorts = [
            x for x in leader_cohorts
            if cohort.validate(targets, cohorts, x)
        ]
        match len(valid_leader_cohorts):
            case 0:
                leader_cohort = prioritized_cohort(cohort, leader_cohorts, targets)
            case 1:
                leader_cohort = valid_leader_cohorts[0]
            case _:
                # too many choices at this time
                continue

        # combine person and their friend's cohorts
        cohorts = leader_cohort.add(cohort, cohorts)
        return sift_cohorts(targets, cohorts)
    return cohorts


def fourth_pass(
        people: list[Person],
        cohorts: list[Cohort],
        targets: schemas.Targets,
        previous_cohorts: list[list[str]]
    ) -> list[Cohort]:
    cohorts = third_pass(people, cohorts, targets)
    new_cohorts = [cohort.to_list() for cohort in cohorts]
    if new_cohorts == previous_cohorts:
        return cohorts
    return fourth_pass(people, cohorts, targets, list(new_cohorts))


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
        strict_friend_cohorts = list(set([
            x.cohort for x in person.preferred_people
            if x not in person.cohort.people
            and (person.cohort.team_number is None
            or x.cohort.team_number is None)
            and x not in person.cohort.user_banned_list
            and person.cohort.validate(targets, cohorts, x.cohort)
        ]))

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
                friend_cohort = prioritized_cohort(person.cohort, strict_friend_cohorts, targets)

        # combine person and their friend's cohorts
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # place cohorts with 0 or 1 possible to leader cohorts
        cohorts = sift_cohorts(targets, cohorts)

        # recurse
        people = [x for x in people if x != person]
    return cohorts


def second_pass(
        people: list[Person],
        cohorts: list[Cohort],
        targets: schemas.Targets,
        must_assign: bool = False,
    ) -> tuple[list[Person], list[Cohort]]:
    for person in people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        # check for validity based on targets + adding to other cohorts
        friend_cohorts = list(set([
            x.cohort for x in person.preferred_people
            if x not in person.cohort.people
            and (person.cohort.team_number is None
            or x.cohort.team_number is None)
            and x not in person.cohort.user_banned_list
        ]))

        strict_friend_cohorts = [
            x for x in friend_cohorts
            if person.cohort.validate(targets, cohorts, x)
        ]

        # take action when a new person has 0 or 1 possible preference
        match len(strict_friend_cohorts):
            case 0:
                # adding person to a cohort with any of their friends
                # will exceed targets
                friend_cohort = prioritized_cohort(person.cohort, friend_cohorts, targets)
            case 1:
                # this is the person's choice
                friend_cohort = strict_friend_cohorts[0]
            case _:
                # 2+ people are reasonable additions
                # too many choices at this time
                if not must_assign:
                    continue
                friend_cohort = prioritized_cohort(person.cohort, strict_friend_cohorts, targets)

        # combine person and their friend's cohorts
        cohorts = friend_cohort.add(person.cohort, cohorts)

        # recurse
        people = [x for x in people if x != person]
        people, cohorts = first_pass(people, cohorts)
        people, cohorts = second_pass(people, cohorts, targets)
        if must_assign:
            people, cohorts = second_pass(people, cohorts, targets, must_assign=must_assign)
        return people, cohorts
    return people, cohorts


def first_pass(people: list[Person], cohorts: list[Cohort]
    ) -> tuple[list[Person], list[Cohort]]:
    current_people = list(people)
    for person in current_people:
        # find new friends
        # leaders cannot cohort with leaders from other teams - only room together
        # remove person preferences rejected by user
        friend_cohorts = list(set([
            x.cohort for x in person.preferred_people
            if x not in person.cohort.people
            and (person.cohort.team_number is None
            or x.cohort.team_number is None)
            and x not in person.cohort.user_banned_list
        ]))

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


@app.post("/file")
def receive_file(file: Annotated[UploadFile, File(description="Raw data.")]) -> schemas.FileReceipt:
    """ Read and interpret file data. """
    all_people = []
    message = ""
    if file.filename.endswith(".xlsx"):
        all_people, leaders, message = read_excel(file)
        print(message)
    elif file.filename.endswith(".json"):
        pass
    else:
        message = "The input must be an XLSX or JSON file."

    # form functional groups to select teams
    cohorts = [x.cohort for x in all_people]

    # assign leaders to cohorts based on team number
    for team_number, leader_list in leaders.items():
        pop_indices = []
        for index, cohort in enumerate(cohorts):
            if any([x in cohort.people for x in leader_list]):
                pop_indices.append(index)
        cohorts = [x for x in cohorts if cohorts.index(x) not in pop_indices]
        cohorts.append(Cohort(leader_list, team_number))

    # remove cohorts with people who don't get assigned to teams
    people = [x for x in all_people if x.cohort.team_number != 0]
    for person in people:
        person.preferred_people = [
            x for x in person.preferred_people
            if x.cohort.team_number != 0
        ]
    cohorts = list(set([x.cohort for x in people]))
    print(len(people))

    # totals
    total_people = len(people)
    team_numbers = [x for x in leaders.keys() if x != 0]
    total_teams = len(team_numbers)
    total_girls = len([x for x in people if x.gender == schemas.Gender.female])
    total_new = len([x for x in people if x.collective == schemas.Collective.new])
    total_newish = len([x for x in people if x.collective == schemas.Collective.newish])
    total_oldish = len([x for x in people if x.collective == schemas.Collective.oldish])
    total_old = len([x for x in people if x.collective == schemas.Collective.old])
    total_18 = len([x for x in people if x.age <= 18])
    total_19_20 = len([x for x in people if x.age >= 19 and x.age <= 20])
    total_21_22 = len([x for x in people if x.age >= 21 and x.age <= 22])
    total_23_24 = len([x for x in people if x.age >= 23 and x.age <= 24])
    total_25 = len([x for x in people if x.age >= 25])

    # targets per team
    targets = schemas.Targets(**{
        "team_size": int(total_people / total_teams),
        "collective_new": int(total_new / total_teams),
        "collective_newish": int(total_newish / total_teams),
        "collective_oldish": int(total_oldish / total_teams),
        "collective_old": int(total_old / total_teams),
        "size_18": int(total_18 / total_teams),
        "size_19_20": int(total_19_20 / total_teams),
        "size_21_22": int(total_21_22 / total_teams),
        "size_23_24": int(total_23_24 / total_teams),
        "size_25": int(total_25 / total_teams),
        "girl_count": int(total_girls / total_teams),
    })

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    new_people = [
        x for x in people
        if x.first_time
        and len(x.preferred_people) != 0
        and all([friend not in x.cohort.people for friend in x.preferred_people])
    ]
    new_people_left, cohorts = first_pass(new_people, cohorts)

    # TODO build a way for the user to specify adds and separates
    user_actions = [
        schemas.UserAction(**{
            "person_1": {
                "first_name": "Peyton",
                "last_name": "Myers",
            },
            "person_2": {
                "first_name": "Ashli",
                "last_name": "Holden",
            },
            "action": "unite",
        }),
        schemas.UserAction(**{
            "person_1": {
                "first_name": "Peyton",
                "last_name": "Myers",
            },
            "person_2": {
                "first_name": "Myha",
                "last_name": "Dukes",
            },
            "action": "unite",
        }),
        schemas.UserAction(**{
            "person_1": {
                "first_name": "Jayla",
                "last_name": "Woodson",
            },
            "person_2": {
                "first_name": "Ali",
                "last_name": "Clements",
            },
            "action": "separate",
        }),
        schemas.UserAction(**{
            "person_1": {
                "first_name": "Jayla",
                "last_name": "Woodson",
            },
            "person_2": {
                "first_name": "Emma",
                "last_name": "Marz",
            },
            "action": "separate",
        }),
    ]

    # enforce user preferences
    for user_action in user_actions:
        person_1, person_2 = None, None
        for person in people:
            # find person_1
            if (person.first_name == user_action.person_1.first_name
                and person.last_name == user_action.person_1.last_name):
                person_1 = person

            # find person_2
            elif (person.first_name == user_action.person_2.first_name
                and person.last_name == user_action.person_2.last_name):
                person_2 = person

            # person_1 and person_2 were found
            if person_1 is not None and person_2 is not None:
                break

        # etiher person_1 or person_2 is missing
        if (person_1 is None or person_2 is None):
            continue

        # leaders from different teams cannot be united
        # leader separation is assumed
        if (person_1.cohort.team_number != None
            and person_2.cohort.team_number != None
            and person_1.cohort.team_number != person_2.cohort.team_number):
            continue

        # combine cohorts
        if user_action.action == schemas.Action.unite:
            # cannot unite if the union is not blessed
            if (person_1 in person_2.cohort.user_banned_list
                or person_2 in person_1.cohort.user_banned_list):
                continue

            # combine person_1 and person_2's cohorts
            cohorts = person_1.cohort.add(person_2.cohort, cohorts)

            # recurse
            new_people_left = [
                x for x in new_people_left
                if all([friend not in x.cohort.people for friend in x.preferred_people])
            ]
            new_people_left, cohorts = first_pass(new_people_left, cohorts)
        elif user_action.action == schemas.Action.separate:
            # separate users if not already united
            if person_1.cohort != person_2.cohort:
                person_1.cohort.user_banned_list.append(person_2)
                person_2.cohort.user_banned_list.append(person_1)
            new_people_left, cohorts = first_pass(new_people_left, cohorts)

    # assign new people with 0 or 1 preference to cohorts while
    # respecting demographic targets and cohorts forming teams
    # restart whenever someone is added to a cohort to capture new information
    new_people_left, cohorts = second_pass(new_people_left, cohorts, targets)

    # assign new people with 2+ preferences
    _, cohorts = second_pass(new_people_left, cohorts, targets, must_assign=True)

    # assign cohorts to cohorts with leaders having 0 or 1 possibilities
    # based on demographic targets
    cohorts = sift_cohorts(targets, cohorts)

    # place the rest of preferred people for each new person
    new_people = [
        person for person in people
        if person.first_time
        and len(person.preferred_people) != 0
        and len(list(set([
            x.cohort for x in person.preferred_people
            if x not in person.cohort.people
            and (person.cohort.team_number is None
            or x.cohort.team_number is None)
            and x not in person.cohort.user_banned_list
            and person.cohort.validate(targets, cohorts, x.cohort)
        ]))) != 0
    ]
    previous_cohorts = [cohort.to_list() for cohort in cohorts]
    cohorts = fourth_pass(new_people, cohorts, targets, previous_cohorts)

    # place people by preferences in order of priorities
    order = [
        schemas.Collective.new,
        schemas.Collective.newish,
        schemas.Collective.oldish,
        schemas.Collective.old,
    ]
    for category in order:
        found_people = [x for x in people if getattr(x, "collective") == category]
        previous_cohorts = [cohort.to_list() for cohort in cohorts]
        cohorts = fourth_pass(found_people, cohorts, targets, previous_cohorts)

    # complete teams
    cohorts = sorted(cohorts, key=lambda x: x.team_size, reverse=True)
    remaining_cohorts = [x for x in cohorts if x.team_number is None]
    for cohort in remaining_cohorts:
        leader_cohorts = sorted([
            x for x in cohorts
            if x.team_number is not None
            and x.team_size < targets.team_size
        ], key=lambda x: x.team_size, reverse=True)
        if len(leader_cohorts) == 0:
            break

        selected_cohort = prioritized_cohort(cohort, leader_cohorts, targets)
        cohorts = selected_cohort.add(cohort, cohorts)


    leader_cohorts = [x for x in cohorts if x.team_number is not None]
    remaining_cohorts = [x for x in cohorts if x.team_number is None]
    for cohort in remaining_cohorts:
        selected_cohort = prioritized_cohort(cohort, leader_cohorts, targets)
        cohorts = selected_cohort.add(cohort, cohorts)


    target_metrics = {priority: (getattr(targets, priority)) for priority in PRIORITIES}
    for k, v in target_metrics.items():
        print(f"{k}: {v}")
    print("-------------------------------------------------------")
    for cohort in sorted(cohorts, key=lambda x: x.team_number):
        print(cohort.team_number)
        metrics = {priority: (getattr(cohort, priority)) for priority in PRIORITIES}
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print({priority: (getattr(cohort, priority)) for priority in PRIORITIES}, cohort.team_number)
        print("-------------------------------------------------------")

    for cohort in sorted(cohorts, key=lambda x: x.team_number):
        print(cohort.to_list(), cohort.team_number)

    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}
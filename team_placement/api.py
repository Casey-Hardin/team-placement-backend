# native imports
from copy import deepcopy
from operator import attrgetter
from typing import Annotated

# third-party imports
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# external imports
from . import schemas
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


def prioritized_friend(person: Person, friend_cohorts: list[Cohort]) -> Person:
    pretend_cohorts = []
    for cohort in deepcopy(friend_cohorts):
        fake_cohort = deepcopy(person.cohort)
        fake_cohort.append(cohort)
        pretend_cohorts.append(fake_cohort)
    pretend_indices = {index: cohort for index, cohort in enumerate(pretend_cohorts)}

    # filter cohorts based on demographic priorities
    # collective status > age > gender status > team count
    priorities = [
        "count_collective_new",
        "count_collective_newish",
        "count_collective_oldish",
        "count_collective_old",
        "count_18",
        "count_19_20",
        "count_21_22",
        "count_23_24",
        "count_25",
        "count_girls",
        "team_size",
    ]

    for priority in priorities:
        min_value = getattr(min(pretend_cohorts, key=attrgetter(priority)), priority)
        pretend_cohorts = [x for x in pretend_cohorts if getattr(x, priority) == min_value]
    index = [key for key, value in pretend_indices.items() if value == pretend_cohorts[0]][0]
    return friend_cohorts[index]


def sift_new_people(
        new_people: list[Person],
        cohorts: list[list[Person]],
        strict: bool = False,
        targets: schemas.Targets | None = None,
        force_assign: bool = False,
    ) -> tuple[list[Person], list[list[Person]]]:
    for person in new_people:
        # team 0 does not get assigned to a team
        # already caught but here for completeness
        if person.cohort.team_number == 0:
            new_people = [x for x in new_people if x != person]
            return sift_new_people(new_people, cohorts)

        # leaders cannot cohort with leaders from other teams - only room together
        friends = [x for x in person.preferred_people if x in person.cohort.people or x.cohort.team_number == None]

        # remove person preferences rejected by user
        friends = [x for x in friends if x not in person.cohort.user_banned_list]

        if strict:
            assert(targets is not None)

            # check for validity based on targets + adding to other cohorts
            strict_friends = [x for x in friends if person.cohort.validate(targets, cohorts, x.cohort)]

            # take action when a new person has 0 or 1 possible preference
            strict_friend_cohorts = list(set([x.cohort for x in strict_friends]))
            match len(strict_friend_cohorts):
                case 0:
                    # adding person to a cohort with any of their friends
                    # will exceed targets
                    friend_cohorts = list(set([x.cohort for x in friends]))
                    friend_cohort = prioritized_friend(person, friend_cohorts)
                case 1:
                    # this is the person's choice
                    friend_cohort = strict_friend_cohorts[0]
                case _:
                    # 2+ people are reasonable additions
                    if force_assign:
                        friend_cohort = prioritized_friend(person, strict_friend_cohorts)
                    else:
                        # too many choices at this time
                        continue
        else:
            # remove new people who were united to one of their preferences by user
            if any([x in friends for x in person.cohort.people]):
                new_people = [x for x in new_people if x != person]
                return sift_new_people(new_people, cohorts)

            # take action when a new person has 0 or 1 possible preference
            friend_cohorts = list(set([x.cohort for x in friends]))
            match len(friend_cohorts):
                case 0:
                    # new person is already in their own cohort
                    new_people = [x for x in new_people if x != person]
                    return sift_new_people(new_people, cohorts)
                case 1:
                    # this is the person's choice
                    friend_cohort = friend_cohorts[0]
                case _:
                    # too many choices at this time
                    continue

        # combine person and their friend's cohorts
        # remove first because appending changes friend's cohort
        cohorts = [x for x in cohorts if x != friend_cohort]
        person.cohort.append(friend_cohort)

        # recurse
        new_people = [x for x in new_people if x != person]
        new_people, cohorts = sift_new_people(new_people, cohorts)
        if strict:
            return sift_new_people(new_people, cohorts, strict, targets, force_assign)
        return new_people, cohorts
    return new_people, cohorts


@app.post("/file")
def receive_file(file: Annotated[UploadFile, File(description="Raw data.")]) -> schemas.FileReceipt:
    """ Read and interpret file data. """
    people = []
    message = ""
    if file.filename.endswith(".xlsx"):
        people, leaders, message = read_excel(file)
        print(message)
    elif file.filename.endswith(".json"):
        pass
    else:
        message = "The input must be an XLSX or JSON file."

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

    # form functional groups to select teams
    cohorts = [x.cohort for x in people]

    # assign leaders to cohorts based on team number
    for team_number, leader_list in leaders.items():
        pop_indices = []
        for index, cohort in enumerate(cohorts):
            if any([x in cohort.people for x in leader_list]):
                pop_indices.append(index)
        cohorts = [x for x in cohorts if cohorts.index(x) not in pop_indices]
        cohorts.append(Cohort(leader_list, team_number))

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    new_people = [x for x in people if x.first_time and x.cohort.team_number != 0]
    new_people_left, cohorts = sift_new_people(new_people, cohorts)

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
        # or one of them does not get placed on a team
        if (person_1 is None or person_1.cohort.team_number == 0
            or person_2 is None or person_2.cohort.team_number == 0):
            continue

        # leaders from different teams cannot be united
        # leader separation is already assumed
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
            # remove first because appending changes friend's cohort
            cohorts = [x for x in cohorts if x != person_2.cohort]
            person_1.cohort.append(person_2.cohort)

            # recurse
            new_people_left, cohorts = sift_new_people(new_people_left, cohorts)
            continue
        elif user_action.action == schemas.Action.separate:
            # separate users if not already united
            if person_2 not in person_1.cohort.people:
                person_1.cohort.user_banned_list.append(person_2)
            if person_1 not in person_2.cohort.people:
                person_2.cohort.user_banned_list.append(person_1)
            new_people_left, cohorts = sift_new_people(new_people_left, cohorts)

    # assign new people with 0 or 1 preference to cohorts while
    # respecting demographic targets and cohorts forming teams
    # restart whenever someone is added to a cohort to capture new information
    new_people_left, cohorts = sift_new_people(new_people_left, cohorts, strict=True, targets=targets)

    # assign new people with 2+ preferences
    new_people_left, cohorts = sift_new_people(new_people_left, cohorts, strict=True, targets=targets, force_assign=True)

    for cohort in cohorts:
        print([f"{x.first_name} {x.last_name}" for x in cohort.people])
    for person in new_people_left:
        print(f"{person.first_name}, {person.last_name}")
    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}
# native imports
from copy import deepcopy
from typing import Annotated

# third-party imports
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# external imports
from . import schemas
from .read_excel import read_excel
from .person import Person


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


def sift_new_people(new_people: list[Person], cohorts: list[list[Person]]) -> tuple[list[Person], list[list[Person]]]:
    for person in new_people:
        # team 0 does not get assigned to a team
        if person.team_number == 0:
            new_people = [x for x in new_people if x != person]
            return sift_new_people(new_people, cohorts)

        # leaders cannot cohort with leaders from other teams - only room together
        friends = [x for x in person.preferred_people if x.team_number in [person.team_number, None]]

        match len(friends):
            case 0:
                cohorts.append([person])
                new_people = [x for x in new_people if x != person]
                return sift_new_people(new_people, cohorts)
            case 1:
                friend = friends[0]
            case _:
                continue

        # combine person and their friend's cohorts
        current_cohorts = deepcopy(cohorts)
        pop_count = 0
        group = [person, friend]
        for index, cohort in enumerate(current_cohorts):
            if any([x in cohort for x in group]):
                group += [x for x in cohort if x not in group]
                cohorts.pop(index - pop_count)
                pop_count += 1

        # determine the new team number
        team_number = person.team_number if person.team_number != None else friend.team_number
        for member in group:
            member.team_number = team_number

        # recurse
        cohorts.append(group)
        new_people = [x for x in new_people if x not in group]
        return sift_new_people(new_people, cohorts)
    return new_people, cohorts


@app.post("/file")
def receive_file(file: Annotated[UploadFile, File(description="Raw data.")]) -> schemas.FileReceipt:
    """ Read and interpret file data. """
    people = []
    message = ""
    if file.filename.endswith(".xlsx"):
        people, message = read_excel(file)
    elif file.filename.endswith(".json"):
        pass
    else:
        message = "The input must be an XLSX or JSON file."

    # totals
    total_people = len(people)
    team_numbers = list(set([x.team_number for x in people if x.team_number not in [None, 0]]))
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
    team_size = int(total_people / total_teams)
    collective_new = int(total_new / total_teams)
    collective_newish = int(total_newish / total_teams)
    collective_oldish = int(total_oldish / total_teams)
    collective_old = int(total_old / total_teams)
    size_18 = int(total_18 / total_teams)
    size_19_20 = int(total_19_20 / total_teams)
    size_21_22 = int(total_21_22 / total_teams)
    size_23_24 = int(total_23_24 / total_teams)
    size_25 = int(total_25 / total_teams)
    girl_count = int(total_girls / total_teams)

    # form functional groups to select teams
    cohorts = []

    # assign leaders to cohorts based on team number
    for team_number in team_numbers:
        cohorts.append([x for x in people if x.team_number == team_number])

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    new_people = [x for x in people if x.first_time]
    new_people_left, cohorts = sift_new_people(new_people, cohorts)

    for cohort in cohorts:
        print([f"{x.first_name} {x.last_name}" for x in cohort])
    print([f"{person.first_name}, {person.last_name}" for person in new_people_left])
    print([f"{person.first_name}, {person.last_name}" for person in people if not any([person in cohort for cohort in cohorts]) and person.first_time])
    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}

    join_options = [x for x in friends if x in join]
    if len(join_options) == 1:
        choice = friend
    for friend in friends:
        if friend in join:
            choice = friend
            break

    # assign person to cohort with first choice that the user isn't preventing
    if choice is None:
        for friend in friends:
            if friend not in separate:
                choice = friend
                break

    # assign user choices
    for person in people:
        user_join = [[
                x for x in people
                if person_id.first_name == x.first_name
                and person_id.last_name == x.last_name
        ][0] for person_id in person.user_preferred_team]

        if user_join == []:
            continue

        current_cohorts = deepcopy(cohorts)
        pop_count = 0
        addends = []
        for index, cohort in enumerate(current_cohorts):
            if any([x in cohort for x in user_join]):
                addends += [x for x in cohort if x not in addends]
                cohorts.pop(index - pop_count)
                pop_count += 1
        if not any([person in x for x in cohorts]):
            cohorts.append([person] + addends)
        else:
            cohort = [x for x in cohorts if person in x][0]
            cohort += [x for x in addends if x not in cohort]


    for cohort in cohorts:
        print([f"{x.first_name} {x.last_name}" for x in cohort])
    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}

    max_preferred = len(max([x.preferred_people for x in new_people], key=len))

    for cohort in cohorts:
        print(cohort[0].leader_team_number, [f"{x.first_name} {x.last_name}" for x in cohort])
    return {"people": people, "message": message}


    cohorts = []
    for person in people:
        group = [person]
        for person_id in person.preferred_people:
            friend = [
                x for x in people
                if person_id.first_name == x.first_name
                and person_id.last_name == x.last_name
            ][0]
            group.append(friend)

        current_cohorts = deepcopy(cohorts)
        pop_count = 0
        for index, cohort in enumerate(current_cohorts):
            if any([x in cohort for x in group]):
                group += [x for x in cohort if x not in group]
                cohorts.pop(index - pop_count)
                pop_count += 1
        cohorts.append(group)
    cohorts.sort(reverse=True, key=len)
    for cohort in cohorts:
        print(len([f"{x.first_name} {x.last_name}" for x in cohort]))




    return {"people": people, "message": message}
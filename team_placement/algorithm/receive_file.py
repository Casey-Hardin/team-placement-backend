@app.post("/receive-file")
def receive_file(
    file: Annotated[UploadFile, File(description="Raw data.")]
) -> list[Person]:
    """Read and interpret file data."""
    all_people = []
    message = ""
    if file.filename.endswith(".xlsx"):
        all_people, leaders, message = read_excel(file)
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
            x for x in person.preferred_people if x.cohort.team_number != 0
        ]
    cohorts = list(set([x.cohort for x in people]))

    # totals
    total_people = len(people)
    team_numbers = [x for x in leaders.keys() if x != 0]
    total_teams = len(team_numbers)
    total_girls = len([x for x in people if x.gender == Gender.female])
    total_new = len([x for x in people if x.collective == Collective.new])
    total_newish = len([x for x in people if x.collective == Collective.newish])
    total_oldish = len([x for x in people if x.collective == Collective.oldish])
    total_old = len([x for x in people if x.collective == Collective.old])
    total_18 = len([x for x in people if x.age <= 18])
    total_19_20 = len([x for x in people if x.age >= 19 and x.age <= 20])
    total_21_22 = len([x for x in people if x.age >= 21 and x.age <= 22])
    total_23_24 = len([x for x in people if x.age >= 23 and x.age <= 24])
    total_25 = len([x for x in people if x.age >= 25])

    # targets per team
    targets = Targets(
        team_size=float(total_people / total_teams),
        collective_new=float(total_new / total_teams),
        collective_newish=float(total_newish / total_teams),
        collective_oldish=float(total_oldish / total_teams),
        collective_old=float(total_old / total_teams),
        size_18=float(total_18 / total_teams),
        size_19_20=float(total_19_20 / total_teams),
        size_21_22=float(total_21_22 / total_teams),
        size_23_24=float(total_23_24 / total_teams),
        size_25=float(total_25 / total_teams),
        girl_count=float(total_girls / total_teams),
    )

    # assign new people with 0 or 1 preference to cohorts
    # restart whenever someone is added to a cohort to capture new information
    new_people = [
        x
        for x in people
        if x.first_time
        and len(x.preferred_people) != 0
        and all([friend not in x.cohort.people for friend in x.preferred_people])
    ]
    new_people_left, cohorts = first_pass(new_people, cohorts)

    for cohort in cohorts:
        if len(cohort.people) > 1:
            print(cohort.to_list(), cohort.team_number)

    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}

    # TODO build a way for the user to specify adds and separates
    user_actions = [
        schemas.UserAction(
            **{
                "person_1": {
                    "first_name": "Peyton",
                    "last_name": "Myers",
                },
                "person_2": {
                    "first_name": "Ashli",
                    "last_name": "Holden",
                },
                "action": "unite",
            }
        ),
        schemas.UserAction(
            **{
                "person_1": {
                    "first_name": "Peyton",
                    "last_name": "Myers",
                },
                "person_2": {
                    "first_name": "Myha",
                    "last_name": "Dukes",
                },
                "action": "unite",
            }
        ),
        schemas.UserAction(
            **{
                "person_1": {
                    "first_name": "Jayla",
                    "last_name": "Woodson",
                },
                "person_2": {
                    "first_name": "Ali",
                    "last_name": "Clements",
                },
                "action": "separate",
            }
        ),
        schemas.UserAction(
            **{
                "person_1": {
                    "first_name": "Jayla",
                    "last_name": "Woodson",
                },
                "person_2": {
                    "first_name": "Emma",
                    "last_name": "Marz",
                },
                "action": "separate",
            }
        ),
    ]

    # enforce user preferences
    for user_action in user_actions:
        person_1, person_2 = None, None
        for person in people:
            # find person_1
            if (
                person.first_name == user_action.person_1.first_name
                and person.last_name == user_action.person_1.last_name
            ):
                person_1 = person

            # find person_2
            elif (
                person.first_name == user_action.person_2.first_name
                and person.last_name == user_action.person_2.last_name
            ):
                person_2 = person

            # person_1 and person_2 were found
            if person_1 is not None and person_2 is not None:
                break

        # etiher person_1 or person_2 is missing
        if person_1 is None or person_2 is None:
            continue

        # leaders from different teams cannot be united
        # leader separation is assumed
        if (
            person_1.cohort.team_number != None
            and person_2.cohort.team_number != None
            and person_1.cohort.team_number != person_2.cohort.team_number
        ):
            continue

        # combine cohorts
        if user_action.action == schemas.Action.unite:
            # cannot unite if the union is not blessed
            if (
                person_1 in person_2.cohort.user_banned_list
                or person_2 in person_1.cohort.user_banned_list
            ):
                continue

            # combine person_1 and person_2's cohorts
            cohorts = person_1.cohort.add(person_2.cohort, cohorts)

            # recurse
            new_people_left = [
                x
                for x in new_people_left
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
        person
        for person in people
        if person.first_time
        and len(
            [
                x.cohort
                for x in person.preferred_people
                if x not in person.cohort.people
                and (person.cohort.team_number is None or x.cohort.team_number is None)
                and x not in person.cohort.user_banned_list
                and person.cohort.validate(targets, cohorts, x.cohort)
            ]
        )
        != 0
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

    # final assigns to all teams
    cohorts = complete_teams(cohorts, targets)

    target_metrics = {priority: (getattr(targets, priority)) for priority in PRIORITIES}
    for k, v in target_metrics.items():
        print(f"{k}: {v}")
    print("-------------------------------------------------------")
    for cohort in sorted(cohorts, key=lambda x: x.team_number):
        print(cohort.team_number)
        metrics = {priority: (getattr(cohort, priority)) for priority in PRIORITIES}
        for k, v in metrics.items():
            print(f"{k}: {v}")
        print(
            {priority: (getattr(cohort, priority)) for priority in PRIORITIES},
            cohort.team_number,
        )
        print("-------------------------------------------------------")

    for cohort in sorted(cohorts, key=lambda x: x.team_number):
        print(cohort.to_list(), cohort.team_number)

    people = [person.to_dict() for person in people]
    return {"people": people, "message": message}

    other_cohorts = sorted(
        [x for x in cohorts if x.team_number is None], key=lambda x: x.team_size
    )
    leader_cohorts = sorted(
        [x for x in cohorts if x.team_number is not None], key=lambda x: x.team_number
    )
    for cohort in other_cohorts + leader_cohorts:
        print(cohort.to_list(), cohort.team_number)

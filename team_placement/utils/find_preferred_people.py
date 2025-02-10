# external imports
from team_placement.schemas import Nicknames, Person


def find_preferred_people(
    nicknames: list[Nicknames], people: list[Person]
) -> list[Person]:
    """
    Applies nicknames to match individuals in each person's preferred people list.

    nicknames
        Nicknames defined for people who may or may not be in the people list.
    people
        People with preferences to be on teams or rooms with other people.

    people
        People with preferences filled in.
    """
    # assign nicknames to all people
    nicknames_dict: dict[str, str] = {}
    for person in people:
        values = next(
            iter(
                [
                    x.nicknames
                    for x in nicknames
                    if person.firstName == x.firstName and person.lastName == x.lastName
                ]
            ),
            [],
        )
        nicknames_dict[person.index] = values

    # decipher preferred people
    for person in people:
        # container to append preferred people
        preferred = person.preferredPeople

        # collect the raw string
        # all comparisons are case-insensitive
        text = person.preferredPeopleRaw
        if text is None:
            continue
        text = text.lower()

        # remove special characters
        omit = {
            "!",
            "?",
        }
        for word in omit:
            text = text.replace(word, "")

        # replace path separators
        text = text.replace(" and ", ", ").replace(" or ", ", ").replace("/", ", ")

        # interpret names from raw strings
        search_array = [x.strip() for x in text.split(",") if x != ""]
        for full_name in search_array:
            # first and last name found
            if " " in full_name and len(full_name.split(" ")) == 2:
                first_name, last_name = full_name.split(" ")

                # match by strictly first and last name
                matches = [
                    x
                    for x in people
                    if first_name == x.firstName.lower()
                    and last_name == x.lastName.lower()
                ]

                if matches == []:
                    # match by first name or nickname
                    # and by first initial of last name
                    matches = [
                        x
                        for x in people
                        if (
                            first_name == x.firstName.lower()
                            or (
                                any(
                                    [
                                        first_name == name.lower()
                                        for name in nicknames_dict[x.index]
                                    ]
                                )
                            )
                        )
                        and x.lastName.lower().startswith(last_name[0])
                    ]
            else:
                # no last names found - build list of names
                names = [full_name]
                if " " in full_name:
                    names = [x for x in full_name.split(" ") if x != ""]

                # match based on first name or nickname
                # a match must also either have the same last name,
                # have also picked this person
                # or be the only individual with that first name or nickname
                matches = []
                for name in names:
                    matches += [
                        x
                        for x in people
                        if (
                            name == x.firstName.lower()
                            or (
                                any(
                                    [
                                        name == nickname.lower()
                                        for nickname in nicknames_dict[x.index]
                                    ]
                                )
                            )
                        )
                        and (
                            person.lastName == x.lastName
                            or (
                                x.preferredPeopleRaw != None
                                and (
                                    person.firstName.lower()
                                    in x.preferredPeopleRaw.lower()
                                    or (
                                        any(
                                            [
                                                nickname.lower()
                                                in x.preferredPeopleRaw.lower()
                                                for nickname in nicknames_dict[
                                                    person.index
                                                ]
                                            ]
                                        )
                                    )
                                )
                            )
                            or len([x for x in people if name == x.firstName.lower()])
                            == 1
                            or len(
                                [
                                    x
                                    for x in people
                                    if any(
                                        [
                                            name == nickname.lower()
                                            for nickname in nicknames_dict[x.index]
                                        ]
                                    )
                                ]
                            )
                            == 1
                        )
                    ]

            # add unique matches to a person's preferred list
            # a person cannot pick themselves
            for match in matches:
                if match.index not in preferred and match.index != person.index:
                    preferred.append(match.index)

        # assign preferred people
        person.preferredPeople = preferred
    return people

from . import schemas


class Person(object):
    # define nicknames - TODO add to config file
    _all_nicknames = [
        {
            "first_name": "Madison",
            "last_name": "Bauman",
            "nicknames": ["Maddy"],
        },
        {
            "first_name": "Madelynne",
            "last_name": "Carden",
            "nicknames": ["Lynnie"],
        },
        {
            "first_name": "Steven",
            "last_name": "Gamauf",
            "nicknames": ["Gam"],
        },
    ]


    def __init__(self, person: schemas.Person):
        self._first_name = person.first_name
        self._last_name = person.last_name

        self._nicknames = None
        for nickname in Person._all_nicknames:
            if (self._first_name == nickname["first_name"]
            and self._last_name == nickname["last_name"]):
                self._nicknames = nickname["nicknames"]

        self._gender = person.gender
        self._preferred_people_raw = person.preferred_people_raw
        self._first_time = person.first_time
        self._age = person.age
        self._collective = person.collective

        self._team_number = person.team_number

        self._preferred_people = []
        self._user_preferred_team = []
        self._user_separate_team = []
        self._user_preferred_room = []
        self._user_separate_room = []

    @property
    def first_name(self):
        return self._first_name


    @property
    def last_name(self):
        return self._last_name


    @property
    def nicknames(self):
        return self._nicknames


    @property
    def gender(self):
        return self._gender


    @property
    def preferred_people_raw(self):
        return self._preferred_people_raw


    @property
    def first_time(self):
        return self._first_time


    @property
    def age(self):
        return self._age


    @property
    def collective(self):
        return self._collective


    @property
    def team_number(self):
        return self._team_number


    @team_number.setter
    def team_number(self, team_number: int | None):
        self._team_number = team_number


    @property
    def preferred_people(self):
        return self._preferred_people


    @preferred_people.setter
    def preferred_people(self, people: list["Person"]):
        self._preferred_people = people


    @property
    def user_preferred_team(self):
        return self._user_preferred_team


    @user_preferred_team.setter
    def user_preferred_team(self, people: list["Person"]):
        self._user_preferred_team = people


    @property
    def user_separate_team(self):
        return self._user_separate_team


    @user_separate_team.setter
    def user_separate_team(self, people: list["Person"]):
        self._user_separate_team = people


    @property
    def user_preferred_room(self):
        return self._user_preferred_room


    @user_preferred_room.setter
    def user_preferred_room(self, people: list["Person"]):
        self._user_preferred_room = people


    @property
    def user_separate_room(self):
        return self._user_separate_room


    @user_separate_room.setter
    def user_separate_room(self, people: list["Person"]):
        self._user_separate_room = people


    def to_dict(self):
        return schemas.Person(**{
            "first_name": self._first_name,
            "last_name": self._last_name,
            "gender": self._gender,
            "preferred_people_raw": self._preferred_people_raw,
            "first_time": self._first_time,
            "age": self._age,
            "collective": self._collective,
            "team_number": self._team_number,
            "preferred_people": [{
                "first_name": x.first_name,
                "last_name": x.last_name,
            } for x in self._preferred_people]
        })
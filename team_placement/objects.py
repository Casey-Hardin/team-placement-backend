# native imports
from operator import attrgetter
from typing import Union

# external imports
from . import schemas
from .constants import PRIORITIES


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

        self._cohort = Cohort(self)
        self._preferred_people = []

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
    def cohort(self):
        return self._cohort


    @cohort.setter
    def cohort(self, cohort: "Cohort"):
        self._cohort = cohort


    @property
    def preferred_people(self):
        return self._preferred_people


    @preferred_people.setter
    def preferred_people(self, people: list["Person"]):
        self._preferred_people = people


    def to_dict(self):
        return schemas.Person(**{
            "first_name": self._first_name,
            "last_name": self._last_name,
            "gender": self._gender,
            "preferred_people_raw": self._preferred_people_raw,
            "first_time": self._first_time,
            "age": self._age,
            "collective": self._collective,
            "preferred_people": [{
                "first_name": x.first_name,
                "last_name": x.last_name,
            } for x in self._preferred_people],
            "team": self._cohort.team_number,
        })


    def __str__(self):
        return f"{self._first_name} {self._last_name}"


class Cohort(object):
    def __init__(self, people: Person | list[Person] = [], team_number: int | None = None):
        self._people = people
        if isinstance(self._people, Person):
            self._people = [self._people]
        for person in self._people:
            person.cohort = self
        self._team_number = team_number

        self._user_banned_list = []


    @property
    def people(self):
        return self._people


    def _set_people(self, people: list[Person]):
        self._people = people


    @property
    def team_number(self):
        return self._team_number


    @team_number.setter
    def team_number(self, team_number: int | None):
        self._team_number = team_number


    @property
    def user_banned_list(self):
        return self._user_banned_list


    @user_banned_list.setter
    def user_banned_list(self, people: Person | list[Person]):
        if isinstance(people, Person):
            self._user_banned_list = [Person]
            return
        self._user_banned_list = people


    def add(self, friend_cohort: "Cohort", cohorts: list["Cohort"] | None = None) -> list["Cohort"] | None:
        if cohorts is not None:
            # remove first because attributes change
            cohorts = [x for x in cohorts if x != friend_cohort]

        # add people from the new cohort to this one
        self._people += friend_cohort.people

        # assign the new cohort for all people
        for person in friend_cohort.people:
            if person.cohort != self:
                person.cohort = self

        # assign new team number
        self._team_number = self._team_number if self._team_number != None else friend_cohort.team_number

        # concatenate banned lists
        self._user_banned_list += friend_cohort.user_banned_list

        return cohorts


    @property
    def team_size(self):
        return len(self._people)


    @property
    def collective_new(self):
        return len([x for x in self._people if x.collective == schemas.Collective.new])


    @property
    def collective_newish(self):
        return len([x for x in self._people if x.collective == schemas.Collective.newish])


    @property
    def collective_oldish(self):
        return len([x for x in self._people if x.collective == schemas.Collective.oldish])


    @property
    def collective_old(self):
        return len([x for x in self._people if x.collective == schemas.Collective.old])


    @property
    def size_18(self):
        return len([x for x in self._people if x.age <= 18])


    @property
    def size_19_20(self):
        return len([x for x in self._people if x.age >= 19 and x.age <= 20])


    @property
    def size_21_22(self):
        return len([x for x in self._people if x.age >= 21 and x.age <= 22])


    @property
    def size_23_24(self):
        return len([x for x in self._people if x.age >= 23 and x.age <= 24])


    @property
    def size_25(self):
        return len([x for x in self._people if x.age >= 25])


    @property
    def girl_count(self):
        return len([x for x in self._people if x.gender == schemas.Gender.female])


    def validate(self, targets: schemas.Targets, cohorts: list["Cohort"], test_cohort: Union["Cohort", None] = None):
        pretend_metrics = schemas.Targets(
            **{priority: getattr(self, priority) for priority in PRIORITIES}
        )
        people = list(self._people)
        team_number = self._team_number
        banned_list = list(self._user_banned_list)
        if test_cohort is not None:
            for priority in PRIORITIES:
                setattr(
                    pretend_metrics,
                    priority,
                    (getattr(pretend_metrics, priority)
                     + getattr(test_cohort, priority)),
                )
            team_number = self._team_number if self._team_number != None else test_cohort.team_number
            people += test_cohort.people
            banned_list += test_cohort.user_banned_list

        if team_number is None:
            leader_cohorts = [x for x in cohorts if x.team_number is not None]
            for cohort in leader_cohorts:
                pretend_cohort = Cohort()
                pretend_cohort._set_people(people)
                pretend_cohort.user_banned_list = banned_list
                if pretend_cohort.validate(targets, cohorts, cohort):
                    return True
            return False

        if test_cohort is None:
            for priority in PRIORITIES:
                if getattr(pretend_metrics, priority) > getattr(targets, priority):
                    return False
            return True

        other_cohorts = [x for x in cohorts if x != test_cohort]
        for priority in PRIORITIES:
            valid = getattr(pretend_metrics, priority) <= getattr(targets, priority)
            min_value = getattr(min(other_cohorts, key=attrgetter(priority)), priority)
            if valid:
                other_cohorts = [
                    x for x in other_cohorts
                    if getattr(x, priority) <=
                    getattr(targets, priority)
                    - getattr(self, priority)
                ]
            else:
                other_cohorts = [x for x in other_cohorts if getattr(x, priority) == min_value]
            if not valid and getattr(test_cohort, priority) != min_value:
                return False
        return True


    def to_list(self):
        return [str(person) for person in self._people]
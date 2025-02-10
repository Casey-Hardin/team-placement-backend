# native imports
from operator import attrgetter
from statistics import stdev
from typing import Union

# external imports
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, Targets
from team_placement.constants import PRIORITIES


class PersonObject(object):
    def __init__(self, person: Person):
        self._index = person.index
        self._order = person.order

        self._first_name = person.firstName
        self._last_name = person.lastName

        self._age = person.age
        self._gender = person.gender
        self._first_time = person.firstTime
        self._collective = person.collective
        self._preferred_people_raw = person.preferredPeopleRaw
        self._preferred_people = person.preferredPeople
        self._preferred = []

        self._leader = person.leader
        self._team = person.team
        self._room = person.room
        self._participant = person.participant

        self._cohort = Cohort(self)

    @property
    def index(self):
        return self._index

    @property
    def order(self):
        return self._order

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def age(self):
        return self._age

    @property
    def gender(self):
        return self._gender

    @property
    def first_time(self):
        return self._first_time

    @property
    def collective(self):
        return self._collective

    @property
    def preferred_people(self):
        return self._preferred_people

    @property
    def preferred(self):
        return self._preferred

    @preferred.setter
    def preferred(self, people: list["PersonObject"]):
        self._preferred = people

    @property
    def leader(self):
        return self._leader

    @leader.setter
    def leader(self, leader: BooleanEnum):
        self._leader = leader

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, team: str):
        self._team = team

    @property
    def room(self):
        return self._room

    @property
    def participant(self):
        return self._participant

    @property
    def cohort(self):
        return self._cohort

    @cohort.setter
    def cohort(self, cohort: "Cohort"):
        self._cohort = cohort

    def to_dict(self):
        return Person(
            index=self._index,
            order=self._order,
            firstName=self._first_name,
            lastName=self._last_name,
            age=self._age,
            gender=self._gender,
            first_time=self._first_time,
            collective=self._collective,
            preferred_people_raw=self._preferred_people_raw,
            preferred_people=self._preferred_people,
            leader=self._leader,
            team=self._team,
            room=self._room,
            participant=self._participant,
        )

    def __str__(self):
        return f"{self._first_name} {self._last_name}"


class Cohort(object):
    def __init__(self, people: PersonObject | list[PersonObject] = []):
        if isinstance(people, PersonObject):
            people = [people]
        self._people = people

        self._team = ""
        if len(people) > 0:
            # set team of cohort
            self._team = people[0].team

            # ensure team is same for all people in cohort
            for person in people:
                person.team = self._team

        for person in self._people:
            person.cohort = self

        self._banned_people: list[PersonObject] = []

    @property
    def people(self):
        return self._people

    def _set_people(self, people: list[PersonObject]):
        self._people = people

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, new_team: str):
        self._team = new_team
        for person in self._people:
            person.team = new_team

    @property
    def banned_people(self):
        return self._banned_people

    @banned_people.setter
    def banned_people(self, people: PersonObject | list[PersonObject]):
        if isinstance(people, PersonObject):
            self._banned_people = [people]
            return
        self._banned_people = people

    @property
    def team_size(self):
        return len(self._people)

    @property
    def collective_new(self):
        return len([x for x in self._people if x.collective == Collective.new])

    @property
    def collective_newish(self):
        return len([x for x in self._people if x.collective == Collective.newish])

    @property
    def collective_oldish(self):
        return len([x for x in self._people if x.collective == Collective.oldish])

    @property
    def collective_old(self):
        return len([x for x in self._people if x.collective == Collective.old])

    @property
    def age_std(self):
        return stdev([x.age for x in self._people])

    @property
    def girl_count(self):
        return len([x for x in self._people if x.gender == Gender.female])

    def add(
        self, friend_cohort: "Cohort", cohorts: list["Cohort"] | None = None
    ) -> list["Cohort"] | None:
        if cohorts is not None:
            # remove first because attributes change
            cohorts = [x for x in cohorts if x != friend_cohort]

        # add people from the new cohort to this one
        self._people += friend_cohort.people

        # assign the new cohort for all people
        for person in friend_cohort.people:
            if person.cohort != self:
                person.cohort = self

        # assign new team
        self.team = self._team if self._team != "" else friend_cohort.team

        # concatenate banned lists
        self._banned_people += friend_cohort.banned_people

        return cohorts

    def validate(
        self,
        targets: Targets,
        cohorts: list["Cohort"],
        test_cohort: Union["Cohort", None] = None,
    ):
        pretend_metrics = Targets(
            **{priority: getattr(self, priority) for priority in PRIORITIES}
        )
        people = list(self._people)
        team = self._team
        banned_list = list(self._banned_people)
        if test_cohort is not None:
            for priority in PRIORITIES:
                setattr(
                    pretend_metrics,
                    priority,
                    (
                        getattr(pretend_metrics, priority)
                        + getattr(test_cohort, priority)
                    ),
                )
            team_number = self._team if self._team != "" else test_cohort.team
            people += test_cohort.people
            banned_list += test_cohort.banned_people

        if team_number is None:
            leader_cohorts = [x for x in cohorts if x.team != ""]
            for cohort in leader_cohorts:
                pretend_cohort = Cohort()
                pretend_cohort._set_people(people)
                pretend_cohort.banned_people = banned_list
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

    def to_list(self):
        return [str(person) for person in self._people]

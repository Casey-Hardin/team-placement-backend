# native imports
from copy import deepcopy
from operator import attrgetter
from statistics import stdev
from typing import Union

# external imports
from team_placement.schemas import BooleanEnum, Collective, Gender, Person, Targets
from team_placement.constants import PRIORITIES


class PersonObject(object):
    def __init__(self, person: Person):
        """
        Initializes a Person object.

        Parameters
        ----------
        person
            Person to initialize.
        """
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
    def index(self) -> int:
        """
        Index of a person.

        Returns
        -------
        int
            Index of a person.
        """
        return self._index

    @property
    def order(self) -> int:
        """
        Order of a person when completing team and room assignments.

        Returns
        -------
        int
            Order of a person.
        """
        return self._order

    @property
    def first_name(self) -> str:
        """
        First name of a person.

        Returns
        -------
        str
            First name of a person.
        """
        return self._first_name

    @property
    def last_name(self) -> str:
        """
        Last name of a person.

        Returns
        -------
        str
            Last name of a person.
        """
        return self._last_name

    @property
    def age(self) -> int:
        """
        Age of a person.

        Returns
        -------
        int
            Age of a person in years.
        """
        return self._age

    @property
    def gender(self) -> Gender:
        """
        Gender of a person.

        Returns
        -------
        Gender
            Gender of a person either male or female.
        """
        return self._gender

    @property
    def first_time(self) -> BooleanEnum:
        """
        First time status of a person.

        Returns
        -------
        BooleanEnum
            First time status of a person
        """
        return self._first_time

    @property
    def collective(self) -> Collective:
        """
        Collective status of a person.

        Returns
        -------
        Collective
            Collective status of a person either new, newish, oldish or old.
        """
        return self._collective

    @property
    def preferred_people(self) -> list[str]:
        """
        Indices of people a person prefers to be associated with.

        Returns
        -------
        list[str]
            Indices of people a person prefers to be associated with.
        """
        return self._preferred_people

    @property
    def preferred(self):
        """
        People objects a person prefers to be associated with.

        Returns
        -------
        list[PersonObject]
            People objects a person prefers to be associated with.
        """
        return self._preferred

    @preferred.setter
    def preferred(self, people: list["PersonObject"]):
        """
        Sets preferred people for a person.

        Parameters
        ----------
        people
            People to set as preferred.
        """
        self._preferred = people

    @property
    def leader(self) -> BooleanEnum:
        """
        Leader status of a person.

        Returns
        -------
        BooleanEnum
            Leader status of a person either yes or no.
        """
        return self._leader

    @leader.setter
    def leader(self, leader: BooleanEnum):
        """
        Sets leader status of a person.

        Parameters
        ----------
        leader
            Leader status to set to a person.
        """
        self._leader = leader

    @property
    def team(self):
        """
        Name of team to which a person belongs.

        Returns
        -------
        str
            Name of team to which a person belongs.
        """
        return self._team

    @team.setter
    def team(self, team: str):
        """
        Sets team to which a person belongs.

        Parameters
        ----------
        team
            New team for a person to belong.
        """
        self._team = team

    @property
    def room(self) -> str:
        """
        Name of a room to which a person will stay.

        Returns
        -------
        str
            Name of a room where a person will stay.
        """
        return self._room

    @property
    def participant(self) -> BooleanEnum:
        """
        Participant status of a person.

        Returns
        -------
        BooleanEnum
            Participant status of a person either yes or no.
        """
        return self._participant

    @property
    def cohort(self) -> "Cohort":
        """
        Group of like-minded people to which a person belongs.

        Returns
        -------
        Cohort
            Group of like-minded people to which a person belongs.
        """
        return self._cohort

    @cohort.setter
    def cohort(self, cohort: "Cohort"):
        """
        Sets cohort to which a person belongs.

        Parameters
        ----------
        cohort
            New cohort for a person to belong.
        """
        self._cohort = cohort

    def to_dict(self) -> dict[str, str | int | BooleanEnum | Collective]:
        """
        Dictionary representation of a person.

        Returns
        -------
        dict[str, str | int | BooleanEnum | Collective]
            Dictionary representation of a person.
        """
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
        """
        String representation of a person.

        Returns
        -------
        str
            String representation of a person.
        """
        return f"{self._first_name} {self._last_name}"


class Cohort(object):
    def __init__(self, people: PersonObject | list[PersonObject] = []):
        """
        Initializes a Cohort object.

        people
            A group of like-minded people.
        """
        if isinstance(people, PersonObject):
            people = [people]
        self._people = people

        self._team = ""
        if len(people) > 0:
            # set team of cohort
            person = next(iter([x for x in people if x.team != ""]), None)
            self._team = person.team if person is not None else ""

            # ensure team is same for all people in cohort
            for person in people:
                person.team = self._team

        self._banned_people: list[PersonObject] = []

    @property
    def people(self) -> list[PersonObject]:
        """
        People in a cohort.

        Returns
        -------
        list[PersonObject]
            People who are like minded.
        """
        return self._people

    def _set_people(self, people: list[PersonObject]):
        """
        Sets people in a cohort.

        Parameters
        ----------
        list[PersonObject]
            People who are like minded.
        """
        self._people = people

    @property
    def team(self) -> str:
        """
        Name of a cohort. All cohorts will eventually have a team.

        Returns
        -------
        str
            Name of a cohort.
        """
        return self._team

    @team.setter
    def team(self, new_team: str):
        """
        Sets the team name for a cohort.

        Parameters
        ----------
        new_team
            New team name for a cohort.
        """
        self._team = new_team
        for person in self._people:
            person.team = new_team

    @property
    def banned_people(self) -> list[PersonObject]:
        """
        People who are not allowed to be in this cohort.

        Returns
        -------
        list[PersonObject]
            People who are not allowed to be in this cohort.
        """
        return self._banned_people

    @banned_people.setter
    def banned_people(self, people: PersonObject | list[PersonObject]):
        """
        Sets people who are not allowed to be in a cohort.

        Parameters
        ----------
        people
            People who are not allowed to be in a cohort.
        """
        if isinstance(people, PersonObject):
            self._banned_people = [people]
            return
        self._banned_people = people

    @property
    def team_size(self) -> int:
        """
        Number of people in a cohort.

        Returns
        -------
        int
            Number of people in a cohort.
        """
        return len(self._people)

    @property
    def collective_new(self) -> int:
        """
        Number of people in a cohort who are new to Collective.

        Returns
        -------
        int
            Number of people in a cohort who are new to Collective.
        """
        return len([x for x in self._people if x.collective == Collective.new])

    @property
    def collective_newish(self) -> int:
        """
        Number of people in a cohort who are newish to Collective.

        Returns
        -------
        int
            Number of people in a cohort who are newish to Collective.
        """
        return len([x for x in self._people if x.collective == Collective.newish])

    @property
    def collective_oldish(self) -> int:
        """
        Number of people in a cohort who are oldish to Collective.

        Returns
        -------
        int
            Number of people in a cohort who are oldish to Collective
        """
        return len([x for x in self._people if x.collective == Collective.oldish])

    @property
    def collective_old(self) -> int:
        """
        Number of people in a cohort who are old to Collective.

        Returns
        -------
        int
            Number of people in a cohort who are old to Collective.
        """
        return len([x for x in self._people if x.collective == Collective.old])

    @property
    def age_mean(self) -> float:
        """
        Average of ages for people in a cohort.

        Returns
        -------
        float
            Average of ages for people in a cohort.
        """
        ages = [x.age for x in self._people]
        return sum(ages) / len(ages) if len(ages) > 0 else 0

    @property
    def age_std(self) -> float:
        """
        Standard deviation of ages for people in a cohort.

        Returns
        -------
        float
            Standard deviation of ages for people in a cohort.
        """
        return stdev([x.age for x in self._people])

    @property
    def girl_count(self) -> int:
        """
        Number of girls in a cohort.

        Returns
        -------
        int
            Number of girls in a cohort.
        """
        return len([x for x in self._people if x.gender == Gender.female])

    def metrics(self) -> Targets:
        """
        Collects targets for a cohort.

        Returns
        -------
        Targets
            Targets for a cohort.
        """
        return Targets(**{priority: getattr(self, priority) for priority in PRIORITIES})

    def add(
        self, friend_cohort: "Cohort", cohorts: list["Cohort"] | None = None
    ) -> list["Cohort"] | None:
        """
        Adds people from a cohort to this one.
        Removes the friend cohort from the list of cohorts.
        Joins banned lists of people.

        Parameters
        ----------
        friend_cohort
            Cohort to add people from.
        cohorts
            List of cohorts to update.

        Returns
        -------
        list[Cohort] | None
            Updated list of cohorts.
        """
        if cohorts is not None:
            # remove first because attributes change
            cohorts = [x for x in cohorts if x != friend_cohort]

        # add people from the new cohort to this one
        self._people += friend_cohort.people

        # assign new cohort for all people
        for person in friend_cohort.people:
            if person.cohort != self:
                person.cohort = self

        # assign new team
        self.team = self._team if self._team != "" else friend_cohort.team

        # concatenate banned lists
        self._banned_people += [
            x for x in friend_cohort.banned_people if x not in self._banned_people
        ]

        return cohorts

    def validate(
        self,
        targets: Targets,
        team_count: int,
        cohorts: list["Cohort"],
        test_cohort: Union["Cohort", None] = None,
    ) -> bool:
        """
        Validates whether joining cohorts is possible while meeting targets.

        Parameters
        ----------
        targets
            Targets for each cohort.
        team_count
            Number of teams to create.
        cohorts
            List of cohorts to validate.
        test_cohort
            Cohort to test for validation.

        Returns
        -------
        bool
            True if joining cohorts will not violate metrics otherwise false.
        """
        # combine people and banned lists
        people = deepcopy(self._people)
        banned_list = deepcopy(self._banned_people)
        if test_cohort is not None:
            people += test_cohort.people
            banned_list += [
                x for x in test_cohort.banned_people if x not in banned_list
            ]

        # working cohort to test
        pretend_cohort = Cohort(people)
        pretend_cohort.banned_people = banned_list

        # values on each target after joining cohorts
        pretend_metrics = pretend_cohort.metrics()

        # cohort must add to a team while meeting targets
        leader_cohorts = [x for x in cohorts if x.team != ""]

        # validation is based on only metrics of this team
        if pretend_cohort.team != "" or len(leader_cohorts) != team_count:
            return all(
                [
                    getattr(pretend_metrics, priority) <= getattr(targets, priority)
                    for priority in PRIORITIES
                ]
            )

        any_leader_validate = any(
            [
                pretend_cohort.validate(targets, cohorts, cohort)
                for cohort in leader_cohorts
            ]
        )
        return any_leader_validate

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

    def to_list(self) -> list[str]:
        """
        Full names of people who belong to a cohort.

        Returns
        -------
        list[str]
            Full names of people who belong to a cohort.
        """
        return [str(person) for person in self._people]

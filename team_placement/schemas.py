# native imports
from enum import Enum

# third-party imports
from pydantic import BaseModel


class Gender(Enum):
    male = "Male"
    female = "Female"


class Collective(Enum):
    new = "This will be my first event."
    newish = "2-5 times"
    oldish = "6-10 times"
    old = "I basically live at Collective."


class PersonIdentifier(BaseModel):
    first_name: str
    last_name: str


class Person(PersonIdentifier):
    gender: Gender
    preferred_people_raw: str | None = None
    first_time: bool
    age: int | None
    collective: Collective
    preferred_people: list[PersonIdentifier] = []
    team: int | None = None


class Action(Enum):
    unite = "unite"
    separate = "separate"


class UserAction(BaseModel):
    person_1: PersonIdentifier
    person_2: PersonIdentifier
    action: Action


class Targets(BaseModel):
    team_size: int
    collective_new: int
    collective_newish: int
    collective_oldish: int
    collective_old: int
    size_18: int
    size_19_20: int
    size_21_22: int
    size_23_24: int
    size_25: int
    girl_count: int


class FileReceipt(BaseModel):
    people: list[Person]
    message: str
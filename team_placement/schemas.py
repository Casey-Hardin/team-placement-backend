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
    team_number: int | None = None
    preferred_people: list[PersonIdentifier] = []
    user_preferred_team: list[PersonIdentifier] = []
    user_separate_team: list[PersonIdentifier] = []
    user_preferred_room: list[PersonIdentifier] = []
    user_separate_room: list[PersonIdentifier] = []


class FileReceipt(BaseModel):
    people: list[Person]
    message: str
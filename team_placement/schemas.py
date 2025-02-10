# native imports
from enum import Enum
from typing import Literal

# third-party imports
from pydantic import BaseModel


class BaseObject(BaseModel):
    index: str


class Cell(BaseModel):
    value: str | int | float | None = None
    colspan: int = 1


class BooleanEnum(str, Enum):
    yes = "Yes"
    no = "No"


class Collective(str, Enum):
    new = "This will be my first event."
    newish = "2-5 times"
    oldish = "6-10 times"
    old = "I basically live at Collective."


class Gender(str, Enum):
    male = "Male"
    female = "Female"


class Nicknames(BaseObject):
    firstName: str
    lastName: str
    nicknames: list[str]


class Person(BaseObject):
    order: int
    firstName: str
    lastName: str
    age: int
    gender: Gender
    firstTime: BooleanEnum
    collective: Collective
    preferredPeopleRaw: str = ""
    preferredPeople: list[str] = []
    leader: BooleanEnum
    team: str = ""
    room: str = ""
    participant: BooleanEnum


class Control(BaseObject):
    order: int
    personIndex: str
    teamInclude: list[str]
    teamExclude: list[str]
    roomInclude: list[str]
    roomExclude: list[str]


class Room(BaseObject):
    name: str
    capacity: int | Literal[""] = ""


class Team(BaseObject):
    name: str


class StartupResponse(BaseModel):
    people: list[Person]
    controls: list[Control]
    teams: list[Team]
    rooms: list[Room]
    nicknames: list[Nicknames]


class Targets(BaseModel):
    team_size: float
    collective_new: float
    collective_newish: float
    collective_oldish: float
    collective_old: float
    age_std: float
    girl_count: float

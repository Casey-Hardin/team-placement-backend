# native imports
import json
import os
from typing import Callable, Type, TypeVar

# third-party imports
from pydantic import BaseModel
import shortuuid

# external imports
from team_placement.constants import (
    CONTROLS_FILE_PATH,
    NICKNAMES_FILE_PATH,
    PEOPLE_FILE_PATH,
    ROOMS_FILE_PATH,
    TEAMS_FILE_PATH,
)
from team_placement.schemas import BaseObject, Control, Nicknames, Person, Room, Team


_T = TypeVar("_T", bound=BaseModel)
Object_T = TypeVar("Object_T", bound=BaseObject)


def collect_objects(model: Type[_T]) -> list[_T]:
    """
    Collects objects from the objects file.

    Parameters
    ----------
    model: Type[BaseObject]
        Pydantic model to validate objects.

    Returns
    -------
    list[Person] | list[Control] | list[Team] | list[Room] | list[Nicknames]
        Objects in the workspace.
    """
    if model == Person:
        path = PEOPLE_FILE_PATH
    elif model == Control:
        path = CONTROLS_FILE_PATH
    elif model == Team:
        path = TEAMS_FILE_PATH
    elif model == Room:
        path = ROOMS_FILE_PATH
    elif model == Nicknames:
        path = NICKNAMES_FILE_PATH
    else:
        message = f"Type {model} is not supported for collection!"
        print(message)
        return []

    if not path.exists():
        message = f"A {path.stem} file does not exist on the local path!"
        print(message)
        return []

    try:
        with open(path, "r") as objects_file:
            all_objects = [model.model_validate(x) for x in json.load(objects_file)]
    except:
        message = f"The {path.stem} file is unreadable. It will be deleted."
        print(message)
        path.unlink()
        return []
    return all_objects


def save_objects(
    model: Type[Object_T],
    objects: list[Object_T],
) -> list[Object_T]:
    """
    Saves objects to the workspace.

    Parameters
    ----------
    objects: list[Person] | list[Control] | list[Team] | list[Room]
        Object(s) to save to the workspace.

    Returns
    -------
    str | None
        Message to return to the frontend.
    list[Person] | list[Control] | list[Team] | list[Room] | list[Nicknames]
        Object(s) to send back to the frontend.
    """
    if model == Person:
        path = PEOPLE_FILE_PATH
    elif model == Control:
        path = CONTROLS_FILE_PATH
    elif model == Team:
        path = TEAMS_FILE_PATH
    elif model == Room:
        path = ROOMS_FILE_PATH
    elif model == Nicknames:
        path = NICKNAMES_FILE_PATH
    else:
        message = f"Type {model} is not supported for saving to the workspace!"
        print(message)
        return message, objects

    for object in objects:
        if object.index == "":
            # create a unique identifier for tire tracking
            index = shortuuid.ShortUUID().random(length=10)
            object.index = index

    if not path.parent.exists():
        os.makedirs(path.parent, exist_ok=True)

    with open(path, "w") as objects_file:
        json.dump([object.model_dump() for object in objects], objects_file, indent=2)

    return objects

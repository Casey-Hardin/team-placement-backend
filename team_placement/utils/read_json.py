# native imports
import json
from typing import Type, TypeVar

# third-party imports
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
import shortuuid


_T = TypeVar("_T", bound=BaseModel)


def read_json(file: UploadFile, model: Type[_T]) -> list[_T]:
    """
    Reads objects data from a json file.

    Parameters
    ----------
    file: UploadFile
        A (.json) file with objects data.

    Returns
    -------
    list[_T]
        Objects collected from the JSON file.
    """
    if not file.filename.endswith(".json"):
        message = "Input must be a json file!"
        print(message)
        raise HTTPException(status_code=410, detail={"message": message})

    try:
        object_dicts = json.load(file.file)
        for index, object_dict in enumerate(object_dicts):
            object_dict["index"] = (
                object_dict["index"]
                if "index" in object_dict
                else shortuuid.ShortUUID().random(length=10)
            )
            object_dict["order"] = (
                object_dict["order"] if "order" in object_dict else index
            )
        all_objects = [model.model_validate(x) for x in object_dicts]
    except:
        message = f"Items could not be read from {file.filename}"
        print(message)
        raise HTTPException(status_code=411, detail={"message": message})

    return all_objects

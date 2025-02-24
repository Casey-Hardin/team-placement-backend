# native imports
from typing import Annotated

# third-party imports
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# external imports
from team_placement.algorithm.run_teams import run_teams
from team_placement.filesystem import collect_objects, save_objects
from team_placement.schemas import (
    Cell,
    Control,
    Nicknames,
    Person,
    Room,
    StartupResponse,
    Team,
)
from team_placement.utils.export_to_excel import export_to_excel
from team_placement.utils.find_preferred_people import find_preferred_people
from team_placement.utils.read_excel import read_excel
from team_placement.utils.read_json import read_json

# create a Fast API application
app = FastAPI()

# add middleware to communicate with ReactJS
origins = [
    "http://localhost:5173",
    "localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def homepage() -> None:
    """Homepage."""
    return {"message": "Hello World"}


@app.post("/export-to-excel")
def export_to_excel_post(
    cells: Annotated[list[list[Cell]], Body(description="Raw Data to send to Excel.")],
) -> None:
    """Sends raw data to an Excel file."""
    return export_to_excel(cells)


@app.get("/get-controls")
async def get_controls() -> list[Control]:
    """
    Collects controls from the workspace.

    Returns
    -------
    list[Control] | None
        Controls in the workspace.
    """
    return collect_objects(model=Control)


@app.get("/get-nicknames")
async def get_nicknames() -> list[Nicknames]:
    """
    Collects nicknames from the workspace.

    Returns
    -------
    list[Nicknames] | None
        Nicknames in the workspace.
    """
    return collect_objects(model=Nicknames)


@app.get("/get-people")
async def get_people() -> list[Person]:
    """
    Collects people from the workspace.

    Returns
    -------
    list[Person] | None
        People in the workspace.
    """
    return collect_objects(model=Person)


@app.get("/get-teams")
async def get_teams() -> list[Team]:
    """
    Collects teams from the workspace.

    Returns
    -------
    list[Team] | None
        Teams in the workspace.
    """
    return collect_objects(model=Team)


@app.get("/get-rooms")
async def get_rooms() -> list[Room]:
    """
    Collects rooms from the workspace.

    Returns
    -------
    list[Room] | None
        Rooms in the workspace.
    """
    return collect_objects(model=Room)


@app.post("/run-teams")
async def run_teams_post(
    people: Annotated[
        list[Person],
        Body(description="People to assign to teams."),
    ],
    controls: Annotated[
        list[Control],
        Body(description="Controls by the user to guide people assignment."),
    ],
    teams: Annotated[
        list[Team],
        Body(description="Teams for people assignment."),
    ],
) -> list[Person] | None:
    """
    Sorts people into teams.

    Returns
    -------
    list[Person] | None
        People with teams assigned otherwise None.
    """
    return run_teams(people, controls, teams)


@app.post("/run-rooms")
async def run_rooms(
    people: Annotated[
        list[Person],
        Body(description="People to assign to rooms."),
    ],
    controls: Annotated[
        list[Control],
        Body(description="Controls by the user to guide people assignment."),
    ],
    rooms: Annotated[
        list[Room],
        Body(description="Rooms for people assignment."),
    ],
) -> list[Person] | None:
    """
    Assigns people to rooms.

    Returns
    -------
    list[Person] | None
        People with rooms assigned otherwise None.
    """
    pass


@app.post("/save-controls")
async def save_controls(
    controls: Annotated[
        list[Control],
        Body(description="New controls."),
    ],
) -> list[Control]:
    """
    Saves controls to a controls file.

    Returns
    -------
    list[Control]
        Controls with index assigned.
    """
    return save_objects(model=Control, objects=controls)


@app.post("/save-nicknames")
async def save_nicknames(
    nicknames: Annotated[
        list[Nicknames],
        Body(description="New nicknames."),
    ],
) -> list[Nicknames]:
    """
    Saves nicknames to a nicknames file.

    Returns
    -------
    list[Nicknames]
        Nicknames with index assigned.
    """
    return save_objects(model=Nicknames, objects=nicknames)


@app.post("/save-people")
async def save_people(
    people: Annotated[
        list[Person],
        Body(description="New people."),
    ],
) -> list[Person]:
    """
    Saves people to a people file.

    Returns
    -------
    list[Person]
        People with index assigned.
    """
    return save_objects(model=Person, objects=people)


@app.post("/save-rooms")
async def save_rooms(
    rooms: Annotated[
        list[Room],
        Body(description="New rooms."),
    ],
) -> list[Room]:
    """
    Saves rooms to a rooms file.

    Returns
    -------
    list[Room]
        Rooms with index assigned.
    """
    return save_objects(model=Room, objects=rooms)


@app.post("/save-teams")
async def save_teams(
    teams: Annotated[
        list[Team],
        Body(description="New teams."),
    ],
) -> list[Team]:
    """
    Saves teams to a teams file.

    Returns
    -------
    list[Team]
        Teams with index assigned.
    """
    return save_objects(model=Team, objects=teams)


@app.get("/startup")
async def startup() -> StartupResponse:
    """
    Collects objects from workspace on startup.

    Returns
    -------
    StartupResponse
        Objects from the workspace.
    """
    people = collect_objects(model=Person)
    controls = collect_objects(model=Control)
    teams = collect_objects(model=Team)
    rooms = collect_objects(model=Room)
    nicknames = collect_objects(model=Nicknames)

    return StartupResponse(
        people=people, controls=controls, teams=teams, rooms=rooms, nicknames=nicknames
    )


@app.post("/upload-file")
def upload_file(
    file: Annotated[UploadFile, File(description="Raw data.")],
) -> list[Person]:
    """
    Read and interpret file data.

    Returns
    -------
    list[Person]
        People collected from the file.
    """
    if file.filename.endswith(".json"):
        return read_json(file, model=Person)
    elif any([file.filename.endswith(x) for x in [".xlsx", ".csv"]]):
        return read_excel(file)
    else:
        message = "Input must be a JSON or Excel file!"
        print(message)
        raise HTTPException(status_code=413, detail={"message": message})


@app.post("/upload-nicknames-file")
def upload_nicknames_file(
    file: Annotated[UploadFile, File(description="Raw data.")],
) -> list[Nicknames]:
    """
    Read and interpret file data.

    Returns
    -------
    list[Nicknames]
        Nicknames collected from the file.
    """
    return read_json(file, model=Nicknames)


@app.post("/find-preferred-people")
def update_people(
    nicknames: Annotated[
        list[Nicknames],
        Body(description="New nicknames."),
    ],
    people: Annotated[
        list[Person],
        Body(description="New people."),
    ],
) -> list[Person]:
    """
    Read and interpret file data.

    Returns
    -------
    list[Person]
        People where preferred people are identified by index.
    """
    people = find_preferred_people(nicknames, people)

    save_objects(model=Person, objects=people)

    return people

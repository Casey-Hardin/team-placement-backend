# native imports
import os
from pathlib import Path

# collective status > age > gender status > team count
PRIORITIES = [
    "collective_new",
    "collective_newish",
    "collective_oldish",
    "collective_old",
    "age_std",
    "girl_count",
    "team_size",
]


LOCAL_PATH = Path("C:/Users") / os.getlogin() / "AppData/Local/Programs/Team Placement"
PEOPLE_FILE_PATH = LOCAL_PATH / "people.json"
CONTROLS_FILE_PATH = LOCAL_PATH / "controls.json"
TEAMS_FILE_PATH = LOCAL_PATH / "teams.json"
ROOMS_FILE_PATH = LOCAL_PATH / "rooms.json"
NICKNAMES_FILE_PATH = LOCAL_PATH / "nicknames.json"

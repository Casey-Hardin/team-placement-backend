from . import schemas


class Cohort(object):
    def __init__(self, people: list[schemas.Person] = None):
        self._people = people

        self._team_number = None


    @property
    def team_number(self):
        return self._team_number
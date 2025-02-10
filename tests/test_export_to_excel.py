# native imports
from unittest.mock import Mock

# third-party imports
from fastapi.testclient import TestClient
import pytest

# external imports
from team_placement.api import app
from team_placement.schemas import Cell


client = TestClient(app)


CELLS_EXAMPLE = [
    [Cell(value="column name")],
    [Cell(value=5)],
]


@pytest.fixture
def my_fs(fs):
    """Use a fake and empty file system."""
    yield fs


@pytest.mark.usefixtures("my_fs")
def test_empty_json():
    """Empty arguments are unprocessible."""
    with TestClient(app) as client:
        response = client.post("/export-to-excel", json={})
    assert response.status_code == 422


@pytest.mark.usefixtures("my_fs")
def test_process(monkeypatch):
    """Projects are in the workspace."""
    export_mock = Mock()
    export_mock.return_value = None
    monkeypatch.setattr("team_placement.api.export_to_excel", export_mock)

    # convert pydantic models to JSON
    cells = []
    for row in CELLS_EXAMPLE:
        row = [x.model_dump() for x in row]
        cells.append(row)

    # collect projects
    response = client.post("/export-to-excel", json=cells)

    assert response.status_code == 200
    export_mock.call_count == 1

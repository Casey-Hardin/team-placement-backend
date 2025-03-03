# native imports
from unittest.mock import Mock

# third-party imports
import pytest

# external imports
from team_placement.algorithm.run_teams import run_teams
from team_placement.schemas import (
    BooleanEnum,
    Collective,
    Control,
    Gender,
    Person,
    Targets,
    Team,
)

CONTROLS = [
    Control(
        index="Control",
        order=1,
        personIndex="Person",
        teamInclude=[""],
        teamExclude=[""],
        roomInclude=[""],
        roomExclude=[""],
    ),
]

PEOPLE = [
    Person(
        index="Person",
        order=1,
        firstName="John",
        lastName="Doe",
        age=25,
        gender=Gender.male,
        firstTime=BooleanEnum.yes,
        collective=Collective.new,
        leader=BooleanEnum.no,
        participant=BooleanEnum.yes,
    )
]

TEAMS = [Team(index="Team", name="Team 1")]


def test_run_teams_empty_people():
    with pytest.raises(Exception):
        run_teams([], CONTROLS, TEAMS)


def test_run_teams_empty_teams():
    with pytest.raises(Exception):
        run_teams(PEOPLE, CONTROLS, [])


def test_process(monkeypatch):
    prepare_people_mock = Mock()
    prepare_people_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.prepare_people_for_teams",
        prepare_people_mock,
    )

    define_targets_mock = Mock()
    define_targets_mock.return_value = Targets(
        team_size=1,
        collective_new=1,
        collective_newish=1,
        collective_oldish=1,
        collective_old=1,
        age_std=1,
        girl_count=1,
    )
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.define_targets", define_targets_mock
    )

    assign_leaders_mock = Mock()
    assign_leaders_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.assign_leaders", assign_leaders_mock
    )

    first_pass_mock = Mock()
    first_pass_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.first_pass", first_pass_mock
    )

    apply_controls_mock = Mock()
    apply_controls_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.apply_controls", apply_controls_mock
    )

    second_pass_mock = Mock()
    second_pass_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.second_pass", second_pass_mock
    )

    sift_cohorts_mock = Mock()
    sift_cohorts_mock.return_value = []
    monkeypatch.setattr(
        "team_placement.algorithm.run_teams.sift_cohorts", sift_cohorts_mock
    )

    run_teams(PEOPLE, CONTROLS, TEAMS)

    prepare_people_mock.call_count == 1
    define_targets_mock.call_count == 1
    assign_leaders_mock.call_count == 1
    first_pass_mock.call_count == 1
    apply_controls_mock.call_count == 1
    second_pass_mock.call_count == 2
    sift_cohorts_mock.call_count == 1

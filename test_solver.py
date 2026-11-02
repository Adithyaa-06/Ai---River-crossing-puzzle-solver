"""Tests for solver.py. Run with:  pytest"""

import pytest

from solver import (
    FarmerWolfGoatCabbage,
    MissionariesCannibals,
    PUZZLES,
    bfs,
    dfs,
)


def test_farmer_bfs_takes_7_crossings():
    result = bfs(FarmerWolfGoatCabbage())
    assert result is not None
    assert result["path_length"] == 7


def test_missionaries_bfs_takes_11_crossings():
    result = bfs(MissionariesCannibals(3, 3, 2))
    assert result is not None
    assert result["path_length"] == 11


@pytest.mark.parametrize("puzzle_name", PUZZLES)
@pytest.mark.parametrize("search", [bfs, dfs])
def test_every_state_in_path_is_valid(puzzle_name, search):
    problem = PUZZLES[puzzle_name]()
    result = search(problem)
    assert result is not None
    path = result["path"]
    assert path[0]["state"] == problem.initial_state
    assert problem.is_goal(path[-1]["state"])
    for step in path:
        assert problem.is_valid(step["state"])


@pytest.mark.parametrize("puzzle_name", PUZZLES)
def test_bfs_is_never_longer_than_dfs(puzzle_name):
    problem = PUZZLES[puzzle_name]()
    assert bfs(problem)["path_length"] <= dfs(problem)["path_length"]


def test_unsolvable_returns_none():
    # 4 missionaries and 4 cannibals cannot cross with a 2-person boat.
    assert bfs(MissionariesCannibals(4, 4, 2)) is None
    assert dfs(MissionariesCannibals(4, 4, 2)) is None

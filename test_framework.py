import pytest
from framework import Framework

@pytest.fixture(scope="module")
def test_framework():
    return Framework("./tester_ai.py", "./tester_ai.py")

def test_framework_init(test_framework):

    # make sure players path is copied right
    for player in test_framework.players:
        assert "./tester" == player

    # make sure the board is right
    for cell in test_framework.board:
        assert "." == cell

def test_framework_run_next_turn(test_framework):

    test_framework.run_next_turn()
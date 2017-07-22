import pytest

from agricola.game import AgricolaGame, Deck
from agricola.ui import _TestUI, _TestUIFinished
from agricola.action import (
    GrainSeeds, VegetableSeeds, Forest, Lessons, MeetingPlace,
    ClayPit, ReedBank, TravelingPlayers, ResourceMarket2P, Fishing)
from agricola.cards import (
    Conjurer, StorehouseKeeper, Harpooner, CattleFeeder)


class _TestAgricolaGame(AgricolaGame):
    def __init__(self, n_players):
        actions = [
            [Lessons(), MeetingPlace(), TravelingPlayers(), ResourceMarket2P(), Fishing()],
            [GrainSeeds(), VegetableSeeds()],
            [Forest(), ClayPit(), ReedBank()]]
        occupations = [Conjurer(), StorehouseKeeper(), Harpooner(), CattleFeeder()]
        minor_improvements = []

        super(_TestAgricolaGame, self).__init__(
            actions, 2, randomize=False,
            occupations=Deck(occupations, 2, shuffle=False),
            minor_improvements=Deck(minor_improvements, 2, shuffle=False),
        )


class GameTestFunction(object):
    def __init__(self, func):
        self.func = func
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True
        self.func(*args, **kwargs)


def test_trigger():
    game = _TestAgricolaGame(2)

    @GameTestFunction
    def _test_before(game):
        assert game.players[0].food == 0
        assert game.players[0].wood == 0
        assert game.players[0].grain == 0

    @GameTestFunction
    def _test_after(game):
        assert game.players[0].food == 1
        assert game.players[0].wood == 1
        assert game.players[0].grain == 1

    assert not _test_before.called
    assert not _test_after.called
    ui = _TestUI(["0", "0", "3", _test_before, "1", _test_after])
    with pytest.raises(_TestUIFinished):
        game.play(ui, first_player=0)
    assert _test_before.called
    assert _test_after.called


if __name__ == "__main__":
    test_trigger()

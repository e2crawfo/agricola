from agricola.game import AgricolaGame, Deck
from agricola.ui import TestUI
from agricola.action import (
    GrainSeeds, VegetableSeeds, Forest, Lessons, MeetingPlace,
    ClayPit, ReedBank, TravelingPlayers, ResourceMarket2P, Fishing)
from agricola.cards import (
    Conjurer, StorehouseKeeper, Harpooner, CattleFeeder)


class TestAgricolaGame(AgricolaGame):
    def __init__(self, n_players):
        actions = [
            [Lessons(), MeetingPlace(), TravelingPlayers(), ResourceMarket2P(), Fishing()],
            [GrainSeeds(), VegetableSeeds()],
            [Forest(), ClayPit(), ReedBank()]]
        occupations = [Conjurer(), StorehouseKeeper(), Harpooner(), CattleFeeder()]
        minor_improvements = []

        super(TestAgricolaGame, self).__init__(
            actions, 2, randomize=False,
            occupations=Deck(occupations, 2, shuffle=False),
            minor_improvements=Deck(minor_improvements, 2, shuffle=False),
        )


def test_trigger():
    game = TestAgricolaGame(2)

    def _test_before(game):
        assert game.players[0].food == 0
        assert game.players[0].wood == 0
        assert game.players[0].grain == 0

    def _test_after(game):
        assert game.players[0].food == 1
        assert game.players[0].wood == 1
        assert game.players[0].grain == 1

    ui = TestUI(["0", "0", "3", _test_before, "1", _test_after])
    game.play(ui, first_player=0)


if __name__ == "__main__":
    test_trigger()

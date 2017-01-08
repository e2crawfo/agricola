from collections import OrderedDict, Counter
from future.utils import with_metaclass, iteritems

from agricola.utils import multiset_satisfy, draw_grid


class Deck(object):
    pass


class Card(object):
    pass


class Hand(object):
    pass


class Occupation(object):
    pass


class Action(object):
    pass


class BuildingMaterial(Action):
    pass


class Fences(Action):
    pass


class PlowField(Action):
    pass


class SowAndBakeBread(Action):
    pass


class Turn(object):
    # O
    pass


class State(object):
    # Consists of the current actions available, who has played which action.
    n_players = 0


class AgricolaException(Exception):
    """ General Agricola exception. """
    pass


class AgricolaNotEnoughResources(AgricolaException):
    """ Raised when a player does not have sufficent
        resources to pay for a requested action.
    """
    pass


class AgricolaLogicError(AgricolaException):
    """ Raised when action is requested that violates
        the rules of Agricola.
    """
    pass


class AgricolaPoorlyFormed(AgricolaLogicError):
    """ Raised when an updated is requested that
        is not well-formed.
    """
    pass


class AgricolaInvalidChoice(AgricolaLogicError):
    """ Raised when an updated is requested that
        is not well-formed.
    """
    pass


class AgricolaImpossible(AgricolaLogicError):
    """ Raised when an update is requested that cannot
        be performed given the current state.
    """
    pass


class Harvest(object):
    # So a Harvest consists of a number of Turns
    pass


def new_game(n_players):
    # Draw and place (first round?) action cards depending on number of players,
    # create player states.
    pass


if __name__ == "__main__":
    # cells = np.tile('.', (3, 5))
    # cells[2, 0:2] = 'R'
    # cells[0, 1:3] = '~'
    # s = draw_grid(cells, (3, 4), [((0, 0), (1, 0)), ((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 1), (1, 1))])
    # print(s)
    #x = Player(food=2, pastures=[Pasture([(1, 0), (1, 1)]), Pasture((1, 2)), Pasture([(1, 3), (1, 4), (2, 3), (2, 4)])], stables=[Stable((0, 2)), Stable((1, 2))], fields=[Field((2, 0)), Field((2, 1))])
    #x = Player(food=2, pastures=[Pasture([(1, 0), (1, 1)]), Pasture((1, 2)), Pasture([(1, 3), (1, 4), (2, 3), (2, 4)])], stables=[Stable((0, 2)), Stable((1, 2))], fields=[Field((2, 0)), Field((2, 2))])
    x = Player()
    print(str(x))
    x.plow_fields([(2, 4), (2, 3)])
    print(str(x))
    print(x.field_spaces)

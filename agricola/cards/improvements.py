import abc
from future.utils import with_metaclass

from agricola.utils import score_mapping, cumsum, generate_resource_trading_candidates
from agricola.choice import (
    SpaceChoice)
from agricola.step import PlowingStep
from agricola import const
import copy
from agricola.errors import (
  AgricolaException, AgricolaNotEnoughResources, AgricolaLogicError,
  AgricolaPoorlyFormed, AgricolaImpossible)

from agricola.cards.base import all_subclasses, Card

def get_minor_improvements():
    mi_classes = all_subclasses(MinorImprovement)

    # DEBUG
    improvements = []
    for i in range(0, 100):
       improvements.append(Field())
    return improvements
    ####################

    return [m() for m in mi_classes]

def get_major_improvements():
    return [Fireplace2(),
            Fireplace3(),
            CookingHearth4(),
            CookingHearth5(),
            Well(),
            ClayOven(),
            StoneOven(),
            Joinery(),
            Pottery(),
            BasketmakersWorkshop()]


class MinorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0
    num_required_occupations = 0
    traveling = False

    def __init__(self):
        pass

    # returns steps
    def check_and_apply(self, player):
        #print("Applying minor improvement {0}.".format(self.name))
        description = "Playing minor improvement {0}".format(self)

        player.change_state(description, cost=self.cost.copy())
        self._check(player)
        return self._apply(player)

    def _check(self, player):
        if len(player.occupations) < self.num_required_occupations:
          raise AgricolaNotEnoughResources("{0} requires {1} occupations. now {2}".format(self.name, self.num_required_occupations, len(player.occupations)))  

    def _apply(self, player):
        pass

    @property
    def card_type(self):
        return "Minor Improvement"

    @property
    def _cost(self):
        return dict()

    @property
    def cost(self):
        return self._cost.copy()

    def victory_points(self, player):
        return self._victory_points

    @abc.abstractproperty
    def deck(self):
        pass

    @abc.abstractproperty
    def text(self):
        pass

class ReedPond(MinorImprovement):
    num_required_occupations = 3
    deck = 'E'
    id = 48
    text = ''
    _victory_points = 1

    def _apply(self, player):
        player.add_future(range(1, 3), 'reed', 1)

# TODO implement
class Quarry(MinorImprovement):
    num_required_occupations = 4
    deck = 'E'
    id = 54
    text = ''
    _victory_points = 2

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class StoneCart(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 2
    deck = 'K'
    id = 142
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class StoneTongs(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'E'
    id = 56
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass


# TODO implement
class Spindle(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'E'
    id = 51
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class BoarBreeding(MinorImprovement):
    _cost = dict(food=1)
    deck = 'K'
    id = 141
    text = ''
    traveling = True

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass


# TODO implement
class Mansion(MinorImprovement):
    _cost = dict(wood=3, clay=3, stone=3, reed=2)
    deck = 'K'
    id = 144
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class Horse(MinorImprovement):
    deck = 'K'
    id = 135
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class LandingNet(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'K'
    id = 126
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class AnimalPen(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 4
    deck = 'E'
    id = 24
    text = ''
    _vicroty_points = 1

    def _apply(self, player, choices):
        player.add_future(range(1, 15), 'food', 2)

# TODO implement
class Manger(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'E'
    id = 23
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class GoosePond(MinorImprovement):
    num_required_occupations = 3
    deck = 'I'
    id = 72
    text = ''
    _victory_points = 1

    def _apply(self, player):
        player.add_future(range(1, 5), 'food', 1)

# TODO implement
class Canoe(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 2
    deck = 'E'
    id = 30
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class DuckPond(MinorImprovement):
    num_required_occupations = 2
    deck = 'K'
    id = 114
    text = ''
    _victory_points = 1

    def _apply(self, player):
        player.add_future(range(1, 4), 'food', 1)

# TODO implement
class Clogs(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'E'
    id = 28
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass
        
# TODO implement
class WoodenStrongbox(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'K'
    id = 123
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class FruitTree(MinorImprovement):
    num_required_occupations = 3
    deck = 'E'
    id = 43
    text = ''
    _victory_points = 1

    def _apply(self, player, choices):
        player.add_future(range(8, 15), 'food', 1, absolute=True)

# TODO implement
class Lumber(MinorImprovement):
    deck = 'K'
    id = 107
    text = ''
    traveling = True

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class CarpPond(MinorImprovement):
    num_required_occupations = 1
    num_required_improvements = 2
    deck = 'E'
    id = 31
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class CornScoop(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'E'
    id = 35
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class CornShef(MinorImprovement):
    deck = 'K'
    id = 129
    text = ''
    traveling = True

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class PrivateForest(MinorImprovement):
    _cost = dict(food=2)
    deck = 'E'
    id = 45
    text = ''

    def _apply(self, player, choices):
        player.add_future([2,4,6,8,10,12,14], 'wood', 1, absolute=True)

# TODO implement
class GrainCart(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 2
    deck = 'I'
    id = 74
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class Loom(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 2
    deck = 'K'
    id = 146
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class FishingRod(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'E'
    id = 12
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

# TODO implement
class SackCart(MinorImprovement):
    _cost = dict(wood=2)
    num_required_occupations = 2
    deck = 'E'
    id = 46
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player, choices):
        pass

class SwanLake(MinorImprovement):
    num_required_occupations = 4
    deck = 'K'
    id = 140
    text = ''
    _victory_points = 2

    def _apply(self, player):
        player.add_future(range(1, 6, 'food', 1))

class Field(MinorImprovement):
    _cost = dict(food=1)
    deck = 'E'
    id = 11
    text = ''
    traveling = True

    def _apply(self, player):
        return [PlowingStep(player)]

class Dovecote(MinorImprovement):
    _cost = dict(store=2)
    deck = 'E'
    id = 57
    text = ''
    _victory_points = 2

    def _apply(self, player):
        player.add_future([10,11,12,13,14], 'food', 1, absolute=True)

# TODO implement
class Bookshelf(MinorImprovement):
    _cost = dict(wood=1)
    num_required_occupations = 3
    deck = 'K'
    id = 112
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

# TODO implement
class Beehive(MinorImprovement):
    num_required_occupations = 3
    num_required_improvements = 2
    deck = 'K'
    id = 108
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

# TODO implement
class WoodCart(MinorImprovement):
    _cost = dict(wood=3)
    num_required_occupations = 3
    deck = 'I'
    id = 79
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

# TODO implement
class HalfTimberedHouse(MinorImprovement):
    _cost = dict(wood=1, clay=1, reed=1, store=2)
    deck = 'E'
    id = 21
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

# TODO implement
class FishTrap(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'I'
    id = 95
    text = ''

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

# TODO implement
class ClayPit(MinorImprovement):
    num_required_occupations = 3
    deck = 'K'
    id = 131
    text = ''
    _victory_points = 1

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

class MajorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0

    def __init__(self):
        pass

    def check_and_apply(self, player):
        #print("Applying major improvement {0}.".format(self.name))
        description = "Playing major improvement {0}".format(self)
        player.change_state(description, cost=self.cost.copy())
        self._apply(player)

    @abc.abstractmethod
    def _apply(self, player):
        raise NotImplementedError()

    @property
    def card_type(self):
        return "Major Improvement"

    @abc.abstractproperty
    def _cost(self):
        return {}

    @property
    def cost(self):
        return self._cost.copy()

    def upgrade_of(self):
        return []

    def victory_points(self, player):
        return self._victory_points

class Fireplace(with_metaclass(abc.ABCMeta, MajorImprovement)):
    _victory_points = 1
    trading_effects = [
        {
            "sheep": -1,
            "food": 2
        },
        {
            "boar": -1,
            "food": 2
        },
        {
            "cattle": -1,
            "food": 3
        },
        {
            "veg": -1,
            "food": 2
        }
    ]

    baking_rates = [
        {
            "grain": -1,
            "food": 2
        }
    ]

    def _apply(self, player):
        player.listen_for_event(self, const.trigger_event_names.resource_trading)
        player.listen_for_event(self, const.trigger_event_names.baking)

    def trigger(self, player, **kwargs):
        if kwargs["event_name"] == const.trigger_event_names.resource_trading:
            return self.resource_choice_filter
        else:
            return self.resource_choice_filter_baking

    def resource_choice_filter(self, player, choice_candidates, executed_action):
        return generate_resource_trading_candidates(player, choice_candidates, self.trading_effects)
    
    def resource_choice_filter_baking(self, player, choice_candidates, executed_action):
        return generate_resource_trading_candidates(player, choice_candidates, self.baking_rates)

class Fireplace2(Fireplace):
    _cost = {'clay': 2}

class Fireplace3(Fireplace):
    _cost = {'clay': 3}

class CookingHearth(with_metaclass(abc.ABCMeta, MajorImprovement)):
    _victory_points = 1

    def upgrade_of(self):
        return [Fireplace]

    trading_effects = [
        {
            "sheep": -1,
            "food": 2
        },
        {
            "boar": -1,
            "food": 3
        },
        {
            "cattle": -1,
            "food": 4
        },
        {
            "veg": -1,
            "food": 3
        }
    ]

    baking_rates = [
        {
            "grain": -1,
            "food": 3
        }
    ]

    def _apply(self, player):
        player.listen_for_event(self, const.trigger_event_names.resource_trading)
        player.listen_for_event(self, const.trigger_event_names.baking)

    def trigger(self, player, **kwargs):
        if kwargs["event_name"] == const.trigger_event_names.resource_trading:
            return self.resource_choice_filter
        else:
            return self.resource_choice_filter_baking

    def resource_choice_filter(self, player, choice_candidates, executed_action):
        return generate_resource_trading_candidates(player, choice_candidates, self.trading_effects)
    
    def resource_choice_filter_baking(self, player, choice_candidates, executed_action):
        return generate_resource_trading_candidates(player, choice_candidates, self.baking_rates)

class CookingHearth4(CookingHearth):
    _cost = {'clay': 4}

class CookingHearth5(CookingHearth):
    _cost = {'clay': 5}


class Well(MajorImprovement):
    victory_points = 4
    _cost = dict(wood=1, stone=3)

    def _apply(self, player):
        player.add_future(range(1, 6), 'food', 1)


class ClayOven(MajorImprovement):
    victory_points = 2
    _cost = dict(clay=3, stone=1)

    def _apply(self, player):
        bread_rates = player.bread_rates[:-1]
        bread_rates.append(5)
        bread_rates = sorted(bread_rates, reverse=True)
        player.bread_rates[:] = bread_rates + player.bread_rates[-1:]

class StoneOven(MajorImprovement):
    victory_points = 3
    _cost = dict(clay=1, stone=3)

    def _apply(self, player):
        bread_rates = player.bread_rates[:-1]
        bread_rates.append(4)
        bread_rates.append(4)
        bread_rates = sorted(bread_rates, reverse=True)
        player.bread_rates[:] = bread_rates + player.bread_rates[-1:]

class Joinery(MajorImprovement):
    _cost = dict(wood=2, stone=2)

    def victory_points(self, player):
        return score_mapping(player.wood, [3, 5, 7], [2, 3, 4, 5])

    def _apply(self, player):
        player.harvest_rates['wood'].append(2)

class Pottery(MajorImprovement):
    _cost = dict(clay=2, stone=2)

    def victory_points(self, player):
        return score_mapping(player.clay, [3, 5, 7], [2, 3, 4, 5])

    def _apply(self, player):
        player.harvest_rates['clay'].append(2)

class BasketmakersWorkshop(MajorImprovement):
    _cost = dict(reed=2, stone=2)

    def victory_points(self, player):
        return score_mapping(player.reed, [1, 3, 5], [2, 3, 4, 5])

    def _apply(self, player):
        player.harvest_rates['reed'].append(3)


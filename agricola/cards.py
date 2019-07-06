import abc
from future.utils import with_metaclass

from .utils import score_mapping, cumsum
from .choice import (
    SpaceChoice)
from .step import PlowingStep
from . import const
import copy
from .errors import (
  AgricolaException, AgricolaNotEnoughResources, AgricolaLogicError,
  AgricolaPoorlyFormed, AgricolaImpossible)


class Card(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractproperty
    def card_type(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def short_name(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{0}({1})>".format(self.name, self.card_type)


def all_subclasses(cls):
    recurse = [
        g for s in cls.__subclasses__() for g in all_subclasses(s)]
    return cls.__subclasses__() + recurse


def get_occupations(n_players):
    
    # DEBUG
    occupations = []
    for i in range(0, 100):
       occupations.append(Woodcutter())
    return occupations
    ####################

    occ_classes = all_subclasses(Occupation)
    return [o() for o in occ_classes if o.min_players <= n_players]


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


class Occupation(with_metaclass(abc.ABCMeta, Card)):
     # returns steps
    def check_and_apply(self, player):
        print("Applying occupation {0}.".format(self.name))

        self._check(player)
        return self._apply(player)

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

    @property
    def card_type(self):
        return "Occupation"

    @abc.abstractproperty
    def deck(self):
        pass

    @abc.abstractproperty
    def min_players(self):
        pass

    @abc.abstractproperty
    def text(self):
        pass

    @property
    def next_choices(self):
        return []

    def victory_points(self, player):
        return 0

# TODO implement
class Lover(Occupation):
    deck = 'K'
    id = 291
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class ReedCollector(Occupation):
    deck = 'E'
    id = 205
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(1, 5), 'reed', 1)

# TODO implement
class PigWhisperer(Occupation):
    deck = 'K'
    id = 302
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class BerryPicker(Occupation):
    deck = 'E'
    id = 152
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class CattleWhisperer(Occupation):
    deck = 'E'
    id = 201
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Cowhead(Occupation):
    deck = 'I'
    id = 240
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Dancer(Occupation):
    deck = 'E'
    id = 212
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class StreetMusician(Occupation):
    deck = 'I'
    id = 257
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Tutor(Occupation):
    deck = 'E'
    id = 174
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class Woodcutter(Occupation):
    deck = 'E'
    id = 176
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.listen_for_event(self, const.trigger_event_names.take_resources_from_action)

    def trigger(self, player, **kwargs):
        return self.resource_choice_filter

    def resource_choice_filter(self, resource_choices):
        result = []
        for resource_choice in resource_choices:
            choice = copy.deepcopy(resource_choice)
            if "wood" in choice["action_resources"] and choice["action_resources"]["wood"] >= 1:
                choice["additional_resources"]["wood"] += 1
            result.append(choice)
        return result

# TODO implement
class Conjurer(Occupation):
    deck = 'E'
    id = 167
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SeasonalWorker(Occupation):
    deck = 'E'
    id = 202
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class ChurchWarden(Occupation):
    deck = 'I'
    id = 227
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class LordOfTheManor(Occupation):
    deck = 'E'
    id = 189
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Cook(Occupation):
    deck = 'E'
    id = 181
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Midwife(Occupation):
    deck = 'I'
    id = 232
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class YeomanFarmer(Occupation):
    deck = 'E'
    id = 165
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Outrider(Occupation):
    deck = 'I'
    id = 261
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class CharcoalBurner(Occupation):
    deck = 'E'
    id = 182
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Chief(Occupation):
    deck = 'E'
    id = 172
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SeedSeller(Occupation):
    deck = 'K'
    id = 296
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Undergardener(Occupation):
    deck = 'E'
    id = 166
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Farmer(Occupation):
    deck = 'E'
    id = 160
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class FieldWatchman(Occupation):
    deck = 'I'
    id = 225
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Patron(Occupation):
    deck = 'E'
    id = 192
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class MasterShepherd(Occupation):
    deck = 'E'
    id = 204
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SheepWhisperer(Occupation):
    deck = 'I'
    id = 250
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Swineherd(Occupation):
    deck = 'E'
    id = 206
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Braggart(Occupation):
    deck = 'E'
    id = 197
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class WoodCollector(Occupation):
    deck = 'I'
    id = 235
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(1, 6), 'wood', 1)

class WoodDeliveryman(Occupation):
    deck = 'K'
    id = 283
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(8, 15), 'wood', 1, absolute=True)

# TODO implement
class Greengrocer(Occupation):
    deck = 'E'
    id = 168
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class ClayWorker(Occupation):
    deck = 'K'
    id = 290
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class ClayDeliveryman(Occupation):
    deck = 'E'
    id = 187
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(8, 15), 'clay', 1, absolute=True)

# TODO implement
class ClayMixer(Occupation):
    deck = 'E'
    id = 188
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class MinorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0
    num_required_occupations = 0
    traveling = False

    def __init__(self):
        pass

    # returns steps
    def check_and_apply(self, player):
        print("Applying minor improvement {0}.".format(self.name))
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
        return [PlowingStep()]

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
        print("Applying major improvement {0}.".format(self.name))
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

    def _apply(self, player):
        player.bread_rates[-1] = max(player.bread_rates[-1], 2)

        cooking_rates = player.cooking_rates

        cooking_rates['veg'] = max(cooking_rates['veg'], 2)
        cooking_rates['sheep'] = max(cooking_rates['sheep'], 2)
        cooking_rates['boar'] = max(cooking_rates['boar'], 2)
        cooking_rates['cattle'] = max(cooking_rates['cattle'], 3)

class Fireplace2(Fireplace):
    _cost = {'clay': 2}

class Fireplace3(Fireplace):
    _cost = {'clay': 3}

class CookingHearth(with_metaclass(abc.ABCMeta, MajorImprovement)):
    _victory_points = 1

    def upgrade_of(self):
        return [Fireplace]

    def _apply(self, player):
        player.bread_rates[-1] = max(player.bread_rates[-1], 3)

        cooking_rates = player.cooking_rates

        cooking_rates['veg'] = max(cooking_rates['veg'], 3)
        cooking_rates['sheep'] = max(cooking_rates['sheep'], 2)
        cooking_rates['boar'] = max(cooking_rates['boar'], 3)
        cooking_rates['cattle'] = max(cooking_rates['cattle'], 4)

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


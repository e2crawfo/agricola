import abc
from future.utils import with_metaclass, iteritems


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
    occ_classes = all_subclasses(Occupation)
    return [o() for o in occ_classes if o.min_players <= n_players]


def get_minor_improvements():
    mi_classes = all_subclasses(MinorImprovement)
    return [m() for m in mi_classes]


def get_major_improvements():
    return [Fireplace(),
            Fireplace(3),
            CookingHearth(),
            CookingHearth(5),
            Well(),
            ClayOven(),
            StoneOven,
            Joinery(),
            Pottery(),
            BasketmakersWorkshop()]


class Occupation(with_metaclass(abc.ABCMeta, Card)):
    def check_and_apply(self, player):
        print("Applying occupation {0}.".format(self.name))

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


class PaperMaker(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Immediately before playing each occupation after this one, you can pay 1 wood total to get 1 food for each occupation you have in front of you.'


class Conjurer(Occupation):
    deck = 'A'
    min_players = 4
    text = 'Each time you use the "Traveling Players" accumulation space, you get an additional 1 wood and 1 grain.'


class StorehouseKeeper(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Each time you use the "Resource Market" action space, you also get your choice of 1 clay or 1 grain.'


class Harpooner(Occupation):
    deck = 'A'
    min_players = 3
    text = 'Each time you use the "Fishing" accumulation space, you can also pay 1 wood to get 1 food for each person you have, and 1 reed.'


class CattleFeeder(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Each time you use the "Grain Seeds" action space, you can also buy 1 cattle for 1 food.'


class AnimalDealer(Occupation):
    deck = 'A'
    min_players = 3
    text = 'Each time you use the "Sheep Market", "Pig Market", or "Cattle Market" accumulation space, you can buy 1 additional animal of the respective type for 1 food.'


class Greengrocer(Occupation):
    deck = 'B'
    min_players = 3
    text = 'Each time you use the "Grain Seeds" action space, you also get 1 vegetable.'


class Lutenist(Occupation):
    deck = 'A'
    min_players = 4
    text = 'Each time another player uses the "Traveling Players accumulation space, you get 1 food and 1 wood. Immediately after, you can buy exactly 1 vegetable for 2 food.'


class Braggart(Occupation):
    deck = 'A'
    min_players = 3
    text = 'During the scoring, you get 2/3/4/5/7/9 bonus points for having at least 5/6/7/8/9/10 improvements in front of you.'


class PigBreeder(Occupation):
    deck = 'A'
    min_players = 4
    text = 'When you play this card, you immediately get 1 wild boar. Your wild boar breed at the end of round 12 (if there is room for new wild boar).'


class BrushwoodCollector(Occupation):
    deck = 'B'
    min_players = 3
    text = 'Each time you renovate or build a room, you can replace the required 1 or 2 reed with a total of 1 wood.'


class Consultant(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card in a 1-/2-/3-/4-player game, you immediately get 2 grain/3 clay/2 reed/2 sheep.'


class WoodCutter(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use a wood accumulation space, you get 1 additional wood.'


class HouseSteward(Occupation):
    deck = 'B'
    min_players = 3
    text = 'If there are still 1/3/6/9 complete rounds left to play, you immediately get 1/2/3/4 wood. During scoring, each player with the most rooms gets 3 bonus points.'


class SheepWhisperer(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Add 2, 5, 8, and 10 to the current round and place 1 sheep on each corresponding round space. At the start of these rounds, you get the sheep.'


class HedgeKeeper(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Build Fences" action, you do not have to pay wood for 3 of the fences you build.'


class FirewoodCollector(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Farmland", "Grain Seeds", "Grain Utilization", or "Cultivation" action space, at the end of that turn, you get 1 wood.'


class ScytheWorker(Occupation):
    deck = 'A'
    min_players = 1
    text = 'When you play this card, you immediately get 1 grain. In the field phase of each harvest, you can harvest 1 additional grain from each of your grain fields.'


class SeasonalWorker(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you get 1 additional grain. From round 6 on, you can choose to get 1 vegetable instead.'


class ClayHutBuilder(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Once you no longer live in a wooden house, place 2 clay on each of the next 5 round spaces. At the start of these rounds, you get that clay.'


class Grocer(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Pile goods in the order listed on the card. At any time, you can buy the top good for 1 food.'
    order = 'wood grain reed stone veg clay reed veg'.split(' ')


class Paster(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Once you are the only player to live in a house with only 2 rooms, you immediately get 3 wood, 2 clay, 1 reed, and 1 stone (only once).'


class AssistantTiller(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you can also plow 1 field.'


class Groom(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card, you immediately get 1 wood. Once you live in a stone house, at the start of each round, you can build exactly 1 stable for 1 wood.'


class MasterBricklayer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you build a major improvement, reduce the stone cost by the number of rooms you have built onto your initial house.'


class Carpenter(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Every new room only costs you 3 of the appropriate build resource and 2 reed (e.g. if you live in a wooden house, 3 wood and 2 reed).'


class StableArchitect(Occupation):
    deck = 'A'
    min_players = 1
    text = 'During scoring, you get 1 bonus point for each unfenced stable in your farmyard.'


class SmallScaleFarmer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'As long as you live in a house with exactly 2 rooms, at the start of each round, you get 1 wood.'


class WallBuilder(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you build at least 1 room, you can place 1 food on each of the next 4 round spaces. At the start of these rounds, you get that food.'


class Cottager(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you can also either build exactly 1 room or renovate your house. Either way, you have to pay the cost.'


class RoughCaster(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you build at least 1 clay room or renovate your house from clay to stone, you also get 3 food.'


class RoofBallaster(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card, you can immediately pay 1 food to get 1 stone for each room you have.'


class Tutor(Occupation):
    deck = 'B'
    min_players = 1
    text = 'During scoring, you get 1 bonus point for each occupation played after this one.'


class OvenFiringBoy(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use a wood accumulation space, you get an additional "Bake Bread" action.'


class OrganicFarmer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'During the scoring, you get 1 bonus point for each pasture containing at least 1 animal while having unused capacity for at least 3 more animals.'


class Manservant(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Once you live in a stone house, palce 3 food on each remaining round space. At the start of these rounds, you get the food.'


class AdoptiveParents(Occupation):
    deck = 'A'
    min_players = 1
    text = 'For 1 food, you can take an action with offspring in the same round you get it. If you do, the offspring does not count as "newborn".'


class Childless(Occupation):
    deck = 'B'
    min_players = 1
    text = 'At the start of each round, if you have at least 3 rooms but only 2 people, you get 1 food and 1 crop of your choice (grain or vegetable).'


class Geologist(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Forest" or "Reed Bank" accumulation space, you also get 1 clay. In games with 3 or more palyers, this also applies to the "Clay Pit".'


class MushroomCollector(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Immediately after each time you use a wood accumulation space, you can exchange 1 wood for 2 food. If you do, place the wood on the accumulation space.'


class Scholar(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Once you live in a stone house, at the start of each round, you can play an occupation for an occupation cost of 1 food or a minor improvement (by paying its cost).'


class PlowDriver(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Once you live in a stone house, at the start of each round, you can pay 1 food to plow 1 field.'


class AnimalTamer(Occupation):
    deck = 'A'
    min_players = 1
    text = 'When you play this card, you immediately get your choice of 1 wood or 1 grain. Instead of just 1 animal total, you can keep any 1 animal in each room of your house.'


class Stonecutter(Occupation):
    deck = 'A'
    min_players = 3
    text = 'Every improvement, room and renovation costs you 1 stone less.'


class Conservator(Occupation):
    deck = 'A'
    min_players = 1
    text = 'You can renovate your wooden house directly to stone without renovating to clay first.'


class FrameBuilder(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you build a room/renovate, but only once per room/action, you can replace exactly 2 clay or 2 stone with 1 wood.'


class SheepWalker(Occupation):
    deck = 'B'
    min_players = 1
    text = 'At any time, you can exchange 1 sheep for either 1 wild boar, 1 vegetable, or 1 stone.'


class Priest(Occupation):
    deck = 'A'
    min_players = 1
    text = 'When you play this card, if you live in a clay house with exactly 2 rooms, you immediately get 3 clay, 2 reed and 2 stone.'


class MinorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0
    travelling = False

    def __init__(self):
        pass

    def check_and_apply(self, player):
        print("Applying minor improvement {0}.".format(self.name))
        description = "Playing minor improvement {0}".format(self)

        change = {k: -v for k, v in iteritems(self.cost)}
        player.change_state(description, change=change)
        self._check(player)
        self._apply(player)

    def _check(self):
        pass

    # TODO
    # @abc.abstractmethod
    # def _apply(self, player):
    #     raise NotImplementedError()
    def _apply(self, player):
        pass

    @property
    def card_type(self):
        return "Minor Improvement"

    @abc.abstractproperty
    def _cost(self):
        return {}

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


class Basket(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'A'
    text = "Immediately after each time you use a wood accumulation space, you can exchange 2 wood for 3 food. If you do, place those 2 wood on the accumulation space."


class ClayEmbankment(MinorImprovement):
    _cost = dict(food=1)
    deck = 'A'
    text = "You immediately get 1 clay for every 2 clay you already have in your supply."
    travelling = True


class LargeGreenhouse(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'A'
    text = "Add 4, 7, and 9 to the current round and place 1 vegetable on each corresponding space. At the start of these rounds, you get that vegetable."

    def _check(player):
        return len(player.occupations) >= 2


class SheperdsCrook(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = "Each time you fence a new pasture covering at least 4 farmyard spaces, you immediately get 2 sheep on this pasture."


class Manger(MinorImprovement):
    _cost = dict(food=2)
    deck = 'A'
    text = "During scoring, if your pastures cover at least 6/7/8/10 farmyard spaces, you get 1/2/3/4 bonus points."


class Mantelpiece(MinorImprovement):
    _cost = dict(stone=1)
    deck = 'B'
    text = "When you play this card, you immediately get 1 bonus point for each complete round left to play. You may no longer renovate your house."

    def victory_points(self, player):
        return -3

    def _check(self, player):
        return player.house_type in ['clay', 'stone']


class HerringPot(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'B'
    text = 'Each time you use the "Fishing" accumulation space, place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'


class SleepingCorner(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'You can use any "Wish for Children" action space even if it is occupied by one other player\'s person.'
    _victory_points = 1

    def _check(self, player):
        return player.grain_fields >= 2


class ClearingSpade(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'At any time, you can move 1 crop from a planted field containing at least 2 crops to an empty field.'


class WoolBlankets(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'During scoring, if you live in a wooden/clay/stone house by then, you get 3/2/0 bonus points.'

    def _check(self, player):
        return player.sheep >= 5


class Scullery(MinorImprovement):
    _cost = dict(wood=1, clay=1)
    deck = 'B'
    text = 'At the start of each round, if you live in a woodn house, you get 1 food.'


class Canoe(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'A'
    text = 'Each time you use the "Fishing" accumulation space, you get an additional 1 food and 1 reed.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 1


class MiningHammer(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'When you play this card, you immediately get 1 food. Each time you renovate, you can also build a stable without paying wood.'


class BigCountry(MinorImprovement):
    _cost = dict()
    deck = 'A'
    text = 'For each complete round left to play, you immediately get 1 bonus point and 2 food.'

    def _check(self, player):
        return not player.empty_spaces


class HardPorcelain(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'B'
    text = 'At any time, you can exchange 2/3/4 clay for 1/2/3 stone.'


class JunkRoom(MinorImprovement):
    _cost = dict(wood=1, clay=1)
    deck = 'A'
    text = 'Each time after you build an improvement, including this one, you get 1 food.'


class DrinkingTrough(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'Each of your pastures (with or without a stable) can hold up to 2 more animals.'


class YoungAnimalMarket(MinorImprovement):
    _cost = dict(sheep=1)
    deck = 'A'
    text = 'You immediately get 1 cattle. (Effectively, you are exchanging 1 sheep for 1 cattle.)'
    travelling = True


class Caravan(MinorImprovement):
    _cost = dict(wood=3, food=3)
    deck = 'B'
    text = 'This card provides room for 1 person.'


class Claypipe(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'In the returning home phase of each round, if you gained at least 7 building resources in the preceding work phase, you get 2 food.'


class LumberMill(MinorImprovement):
    _cost = dict(stone=2)
    deck = 'A'
    text = 'Every improvement costs you 1 wood less.'
    _victory_points = 2

    def _check(self, player):
        return len(player.occupations) <= 3


class LoamPit(MinorImprovement):
    _cost = dict(food=1)
    deck = 'B'
    text = 'Each time you use the "Day Laborer" action space, you also get 3 clay.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 3


class ShiftingCultivation(MinorImprovement):
    _cost = dict(food=2)
    deck = 'A'
    text = 'Immediately plow 1 field.'
    travelling = True


class PondHut(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) == 2


class Loom(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'In the field phase of each harvest, if you have at least 1/4/7 sheep, you get 1/2/3 food. During scoring, you get 1 bonus point for every 3 sheep.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 2


class MoldboardPlow(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 2 field tiles on this card. Twice this game, when you use the "Farmland" action space, you can also plow 1 field from this card.'

    def _check(self, player):
        return len(player.occupations) >= 1


class MiniPasture(MinorImprovement):
    _cost = dict(food=2)
    deck = 'B'
    text = 'Immediately fence a farmyard space, without paying wood for the fences. (If you already have pastures, the new one must be adjacent to an existing one.)'
    travelling = True


class Pitchfork(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'Each time you use the "Grain Seeds" action space, if the "Farmland" action space is occupied, you also get 3 food.'


class Lasso(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'B'
    text = 'You can place exactly two people immediately after one another if at least one of them use the "Sheep Market", "Pig Market", or "Cattle Market" accumulation space.'


class Bottles(MinorImprovement):
    # TODO: cost depends on the state of the player.
    _cost = dict(clay=2, food=2)
    deck = 'B'
    text = 'For each person you have, you must pay an additional 1 clay and 1 food to play this card.'
    _victory_points = 4


class ThreeFieldRotation(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'At the start of the field phase of each harvest, if you have at least 1 grain field, 1 vegetable field, and 1 empty field, you get 3 food.'

    def _check(self, player):
        return len(player.occupations) >= 3


class MarketStall(MinorImprovement):
    _cost = dict(grain=1)
    deck = 'B'
    text = 'You immediately get 1 vegetable. (Effectively, you are exchanging 1 grain for 1 vegetable.)'
    travelling = True


class Beanfield(MinorImprovement):
    _cost = dict(food=1)
    deck = 'B'
    text = 'This card is a field that can only grow vegetables.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 2


class ButterChurn(MinorImprovement):
    _cost = dict(food=1)
    deck = 'B'
    text = 'In the field phase of each harvest, you get 1 food for every 3 sheep and 1 food for every 2 cattle you have.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) <= 3


class CarpentersParlor(MinorImprovement):
    _cost = dict(wood=1, stone=1)
    deck = 'B'
    text = 'Wooden rooms only cost you 2 wood and 2 reed each.'


class AcornBasket(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'B'
    text = 'Place 1 wild boar on each of the next 2 round spaces. At the start of these rounds you get the wild boar.'

    def _check(self, player):
        return len(player.occupations) >= 3


class StrawberryPatch(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'Place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'
    _victory_points = 2

    def _check(self, player):
        return player.veg_fields >= 2


class CornScoop(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use the "Grain Seeds" action space, you get 1 additional grain.'


class RammedClay(MinorImprovement):
    _cost = dict()
    deck = 'A'
    text = 'When you play this card, you immediately get 1 clay. You can use clay instead of wood to build fences.'


class ThreshingBoard(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use the "Farmland", or "Cultivation" action space, you get an additional "Bake Bread" action.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 2


class DutchWindmill(MinorImprovement):
    _cost = dict(wood=2, stone=2)
    deck = 'A'
    text = 'Each time you take a "Bake Bread" action in a round immediately following a harvest, you get 3 additional food.'
    _victory_points = 2


class StoneTongs(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use a stone accumulation space, you get 1 additional stone.'


class ThickForest(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 1 wood on each remaining even-numbered round space. At the start of these rounds, you get the wood.'

    def _check(self, player):
        return player.clay >= 5


class BreadPaddle(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'When you play this card, you immediately get 1 food. For each occupation you play, you get an additional "Bake Bread" action.'


class Handplow(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Add 5 to the urrent round and place 1 field tile on the corresponding round space. At the start of that round, you can plow the field.'


class MilkJug(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'Each time any player (including you) uses the "Cattle Market" accumulation space, you get 3 food, and each other player gets 1 food.'


class Brook(MinorImprovement):
    _cost = dict()
    deck = 'B'
    text = 'Each time you use one of the four action spaces above the "Fishing" accumulation space, you get 1 additional food.'

    def _check(self, player):
        # TODO: one of your people have to be on the fishing action space
        pass


class SackCart(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 1 grain each on the remaining spaces for rounds 5, 8, 11, and 14. At the start of these rounds, you get the grain.'

    def _check(self, player):
        return len(player.occupations) >= 2


class MajorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0

    def __init__(self):
        pass

    def check_and_apply(self, player):
        print("Applying major improvement {0}.".format(self.name))
        description = "Playing major improvement {0}".format(self)
        change = {k: -v for k, v in iteritems(self.cost)}
        player.change_state(description, change=change)
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


class Fireplace(MajorImprovement):
    _victory_points = 1
    _cost = {'clay': 2}

    def __init__(self, clay=2):
        self._cost = {'clay': clay}

    @property
    def name(self):
        return "Fireplace(clay={0})".format(self._cost['clay'])

    def _apply(self, player):
        player.bread_rates[-1] = max(player.bread_rates[-1], 2)

        cr = player.cooking_rates

        cr['veg'] = max(cr['veg'], 2)
        cr['sheep'] = max(cr['sheep'], 2)
        cr['boar'] = max(cr['boar'], 2)
        cr['cattle'] = max(cr['cattle'], 3)


class CookingHearth(MajorImprovement):
    _victory_points = 1
    _cost = {'clay': 4}

    def __init__(self, clay=4):
        self._cost = {'clay': clay}

    @property
    def name(self):
        return "CookingHearth(clay={0})".format(self._cost['clay'])

    def upgrade_of(self):
        return [Fireplace]

    def _apply(self, player):
        player.bread_rates[-1] = max(player.bread_rates[-1], 3)

        cr = player.cooking_rates

        cr['veg'] = max(cr['veg'], 3)
        cr['sheep'] = max(cr['sheep'], 2)
        cr['boar'] = max(cr['boar'], 3)
        cr['cattle'] = max(cr['cattle'], 4)


class Well(MajorImprovement):
    victory_points = 4
    _cost = dict(wood=1, stone=3)

    def _apply(self, player):
        # TODO
        pass


class ClayOven(MajorImprovement):
    victory_points = 2
    _cost = dict(clay=3, stone=1)

    def _apply(self, player):
        br = player.bread_rates[:-1]
        br.append(5)
        br = sorted(br, reverse=True)
        player.bread_rates[:] = br + player.bread_rates[-1:]


class StoneOven(MajorImprovement):
    victory_points = 3
    _cost = dict(clay=1, stone=3)

    def _apply(self, player):
        br = player.bread_rates[:-1]
        br.append(4)
        br.append(4)
        br = sorted(br, reverse=True)
        player.bread_rates[:] = br + player.bread_rates[-1:]


class Joinery(MajorImprovement):
    _cost = dict(wood=2, stone=2)

    def victory_points(self, player):
        vp = 2
        if player.wood >= 3:
            vp += 1
        if player.wood >= 5:
            vp += 1
        if player.wood >= 7:
            vp += 1
        return vp

    def _apply(self, player):
        player.harvest_rates['wood'].append(2)


class Pottery(MajorImprovement):
    _cost = dict(clay=2, stone=2)

    def victory_points(self, player):
        vp = 2
        if player.clay >= 3:
            vp += 1
        if player.clay >= 5:
            vp += 1
        if player.clay >= 7:
            vp += 1
        return vp

    def _apply(self, player):
        player.harvest_rates['clay'].append(2)


class BasketmakersWorkshop(MajorImprovement):
    _cost = dict(reed=2, stone=2)

    def victory_points(self, player):
        vp = 2
        if player.reed >= 1:
            vp += 1
        if player.reed >= 3:
            vp += 1
        if player.reed >= 5:
            vp += 1
        return vp

    def _apply(self, player):
        player.harvest_rates['reed'].append(3)

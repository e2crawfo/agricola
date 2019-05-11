import abc
from future.utils import with_metaclass


from agricola.utils import score_mapping, cumsum
from agricola.choice import (
    YesNoChoice, DiscreteChoice, CountChoice, ListChoice, SpaceChoice)


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

    def victory_points(self, player):
        return 0


class PaperMaker(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Immediately before playing each occupation after this one, you can pay 1 wood total to get 1 food for each occupation you have in front of you.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Lessons', before=True)
        player.listen_for_event(self, 'Action: Lessons3P', before=True)
        player.listen_for_event(self, 'Action: Lessons4P', before=True)

    def trigger(self, player, **kwargs):
        if player.wood >= 1:
            desc = ("PaperMaker (before): Pay 1 wood to receive 1 food "
                    "for each of your people?")
            use = player.game.get_choice(player, YesNoChoice(desc))
            if use:
                player.change_state(
                    "PaperMaker effect.",
                    cost=dict(wood=1),
                    change=dict(food=len(player.occupations)))


class Conjurer(Occupation):
    deck = 'A'
    min_players = 4
    text = 'Each time you use the "Traveling Players" accumulation space, you get an additional 1 wood and 1 grain.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: TravelingPlayers')

    def trigger(self, player, **kwargs):
        player.add_resources(grain=1, wood=1)


class StorehouseKeeper(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Each time you use the "Resource Market" action space, you also get your choice of 1 clay or 1 grain.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: ResourceMarket2P')
        player.listen_for_event(self, 'Action: ResourceMarket3P')
        player.listen_for_event(self, 'Action: ResourceMarket4P')

    def trigger(self, player, **kwargs):
        choice = player.game.get_choice(
            player, DiscreteChoice(('clay', 'grain')),
            "StorehouseKeeper: Get 1 clay or 1 grain?")
        player.add_resources(**{choice: 1})


class Harpooner(Occupation):
    deck = 'A'
    min_players = 3
    text = 'Each time you use the "Fishing" accumulation space, you can also pay 1 wood to get 1 food for each person you have, and 1 reed.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Fishing')

    def trigger(self, player, **kwargs):
        if player.wood >= 1:
            desc = ("Harpooner: Pay 1 wood to receive 1 food "
                    "for each of your people, and 1 reed?")
            use = player.game.get_choice(player, YesNoChoice(desc))
            if use:
                player.change_state(
                    "Harpooner effect.",
                    cost=dict(wood=1),
                    change=dict(food=player.people, reed=1))


class CattleFeeder(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Each time you use the "Grain Seeds" action space, you can also buy 1 cattle for 1 food.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: GrainSeeds')

    def trigger(self, player, action):
        if player.food >= 1:
            desc = "CattleFeeder: Buy 1 cattle for 1 food?"
            choice = player.game.get_choice(player, YesNoChoice(desc))
            if choice:
                player.add_animals(cattle=1)
                player.add_resources(food=-1)


class AnimalDealer(Occupation):
    deck = 'A'
    min_players = 3
    text = 'Each time you use the "Sheep Market", "Pig Market", or "Cattle Market" accumulation space, you can buy 1 additional animal of the respective type for 1 food.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: SheepMarket')
        player.listen_for_event(self, 'Action: BoarMarket')
        player.listen_for_event(self, 'Action: CattleMarket')

    def trigger(self, player, action):
        animal = {
            'SheepMarket': 'sheep',
            'BoarMarket': 'boar',
            'CattleMarket': 'cattle'}[action.__class__.__name__]

        if player.food >= 1:
            desc = "AnimalDealer: Buy 1 additional {} for 1 food?".format(animal)
            choice = player.game.get_choice(player, YesNoChoice(desc))
            if choice:
                player.add_animals(**{animal: 1})
                player.add_resources(food=-1)


class Greengrocer(Occupation):
    deck = 'B'
    min_players = 3
    text = 'Each time you use the "Grain Seeds" action space, you also get 1 vegetable.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: GrainSeeds')

    def trigger(self, player, **kwargs):
        player.add_resources(veg=1)


class Lutenist(Occupation):
    deck = 'A'
    min_players = 4
    text = 'Each time another player uses the "Traveling Players" accumulation space, you get 1 food and 1 wood. Immediately after, you can buy exactly 1 vegetable for 2 food.'

    def check_and_apply(self, player):
        player.game.listen_for_event(self, 'Action: TravelingPlayers')
        self.player = player

    def trigger(self, player, **kwargs):
        if player != self.player:
            self.player.add_resources(food=1, veg=1)
            if self.player.food >= 2:
                desc = "Lutenist: Buy 1 vegetable for 2 food?"
                use = self.player.game.get_choice(self.player, YesNoChoice(desc))
                if use:
                    self.player.change_state(cost=dict(food=2), change=dict(veg=1))


class Braggart(Occupation):
    deck = 'A'
    min_players = 3
    text = 'During the scoring, you get 2/3/4/5/7/9 bonus points for having at least 5/6/7/8/9/10 improvements in front of you.'

    def victory_points(self, player):
        imps = len(player.major_improvements) + len(player.minor_improvements)
        return score_mapping(imps, [5, 6, 7, 8, 9, 10], [0, 2, 3, 4, 5, 7, 9])


class PigBreeder(Occupation):
    deck = 'A'
    min_players = 4
    text = 'When you play this card, you immediately get 1 wild boar. Your wild boar breed at the end of round 12 (if there is room for new wild boar).'

    def check_and_apply(self, player):
        player.add_resources(boar=1)

    def trigger(self, player, **kwargs):
        pass


class BrushwoodCollector(Occupation):
    deck = 'B'
    min_players = 3
    text = 'Each time you renovate or build a room, you can replace the required 1 or 2 reed with a total of 1 wood.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'build_room')
        player.listen_for_event(self, 'renovate')

    def trigger(self, player, **kwargs):
        desc = "BrushwoodCollector: 1 wood in place of all reed?"
        choice = player.game.get_choice(player, YesNoChoice(desc))
        # TODO


class Consultant(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card in a 1-/2-/3-/4-player game, you immediately get 2 grain/3 clay/2 reed/2 sheep.'

    def check_and_apply(self, player):
        n_players = player.game.n_players
        if n_players == 1:
            player.add_resources(grain=2)
        elif n_players == 2:
            player.add_resources(clay=3)
        elif n_players == 3:
            player.add_resources(reed=2)
        else:
            player.add_resources(sheep=2)


class WoodCutter(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use a wood accumulation space, you get 1 additional wood.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: Grove')
        player.listen_for_event(self, 'Action: Copse')

    def trigger(self, player, **kwargs):
        player.add_resources(wood=1)


class HouseSteward(Occupation):
    deck = 'B'
    min_players = 3
    text = 'If there are still 1/3/6/9 complete rounds left to play, you immediately get 1/2/3/4 wood. During scoring, each player with the most rooms gets 3 bonus points.'

    def check_and_apply(self, player):
        wood = score_mapping(player.game.rounds_remaining, [1, 3, 6, 9], [0, 1, 2, 3, 4])
        player.add_resources(wood=wood)


class SheepWhisperer(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Add 2, 5, 8, and 10 to the current round and place 1 sheep on each corresponding round space. At the start of these rounds, you get the sheep.'

    def check_and_apply(self, player):
        player.add_future([2, 5, 8, 10], 'sheep', 1)


class HedgeKeeper(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Build Fences" action, you do not have to pay wood for 3 of the fences you build.'


class FirewoodCollector(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Farmland", "Grain Seeds", "Grain Utilization", or "Cultivation" action space, at the end of that turn, you get 1 wood.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Farmland')
        player.listen_for_event(self, 'Action: GrainSeeds')
        player.listen_for_event(self, 'Action: GrainUtilization')
        player.listen_for_event(self, 'Action: Cultivation')

    def trigger(self, player, **kwargs):
        player.add_resources(wood=1)


class ScytheWorker(Occupation):
    deck = 'A'
    min_players = 1
    text = 'When you play this card, you immediately get 1 grain. In the field phase of each harvest, you can harvest 1 additional grain from each of your grain fields.'

    def check_and_apply(self, player):
        player.add_resources(grain=1)
        player.listen_for_event(self, 'Action: TravelingPlayers')


class SeasonalWorker(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you get 1 additional grain. From round 6 on, you can choose to get 1 vegetable instead.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: DayLaborer')

    def trigger(self, player, **kwargs):
        # TODO: choose once its round 6
        player.add_resources(grain=1)


class ClayHutBuilder(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Once you no longer live in a wooden house, place 2 clay on each of the next 5 round spaces. At the start of these rounds, you get that clay.'

    def check_and_apply(self, player):
        if player.house_type != 'wood':
            player.add_future(range(1, 6), 'clay', 2)
        else:
            player.listen_for_event(self, 'renovation')

    def trigger(self, player, **kwargs):
        player.add_future(range(1, 6), 'clay', 2)
        player.stop_listening(self, 'renovation')


class Grocer(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Pile goods in the order listed on the card. At any time, you can buy the top good for 1 food.'
    order = 'wood grain reed stone veg clay reed veg'.split(' ')


class Pastor(Occupation):
    deck = 'B'
    min_players = 4
    text = 'Once you are the only player to live in a house with only 2 rooms, you immediately get 3 wood, 2 clay, 1 reed, and 1 stone (only once).'
    player = None

    def check_and_apply(self, player):
        self.player = player

        player.game.listen_for_event(self, 'build_room')
        self.trigger()

    def trigger(self, **kwargs):
        player = self.player
        assert player is not None

        if player.rooms > 2:
            player.game.stop_listening(self, 'build room')

        other_players = player.game.players + []
        other_players.remove(player)
        applies = all(p.rooms > 2 for p in other_players)
        if applies:
            player.add_resources(wood=3, clay=2, reed=1, stone=1)
            player.game.stop_listening(self, 'build room')


class AssistantTiller(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you can also plow 1 field.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: DayLaborer')

    def trigger(self, player, **kwargs):
        desc = "AssistantTiller: Plow a field?"
        plow_field = player.game.get_choice(player, YesNoChoice(desc))
        if plow_field:
            space_to_plow = player.game.get_choices(player, SpaceChoice("Space to plow."))
            player.plow_fields(space_to_plow)


class Groom(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card, you immediately get 1 wood. Once you live in a stone house, at the start of each round, you can build exactly 1 stable for 1 wood.'

    def check_and_apply(self, player):
        player.add_resources(wood=1)
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.house_type == 'stone':
            desc = "Groom: Build a stable for 1 wood?"
            build_stable = player.game.get_choice(player, YesNoChoice(desc))
            if build_stable:
                stable_loc = player.game.get_choices(player, SpaceChoice("Stable location."))
                player.build_stables(stable_loc, 1)


class MasterBricklayer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you build a major improvement, reduce the stone cost by the number of rooms you have built onto your initial house.'

    def check_and_apply(self, player):
        # TODO
        pass


class Carpenter(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Every new room only costs you 3 of the appropriate build resource and 2 reed (e.g. if you live in a wooden house, 3 wood and 2 reed).'


class StableArchitect(Occupation):
    deck = 'A'
    min_players = 1
    text = 'During scoring, you get 1 bonus point for each unfenced stable in your farmyard.'

    def victory_points(self, player):
        pass


class SmallScaleFarmer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'As long as you live in a house with exactly 2 rooms, at the start of each round, you get 1 wood.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.rooms == 2:
            player.add_resources(wood=1)


class WallBuilder(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you build at least 1 room, you can place 1 food on each of the next 4 round spaces. At the start of these rounds, you get that food.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'build_room')

    def trigger(self, player, **kwargs):
        player.add_future(range(1, 5), 'food', 1)


class Cottager(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Day Laborer" action space, you can also either build exactly 1 room or renovate your house. Either way, you have to pay the cost.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: DayLaborer')

    def trigger(self, player, **kwargs):
        choice = DiscreteChoice(
            ['Build room', 'Renovate house', 'Do nothing'],
            "Cottager effect")
        action = player.game.get_choice(player, choice)

        if action == choice.options[0]:
            choice = SpaceChoice("Room location.")
            room_loc = player.game.get_choice(player, choice)
            player.build_rooms(room_loc)
        elif action == choice.options[0]:
            choice = DiscreteChoice(
                player.valid_house_upgrades, "Choose new house material."),
            material = player.game.get_choice(player, choice)
            player.upgrade_house(material)
        else:
            pass


class RoughCaster(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Each time you build at least 1 clay room or renovate your house from clay to stone, you also get 3 food.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'build_room')
        player.listen_for_event(self, 'renovate')

    def trigger(self, player, event_name):
        success = event_name == 'build room' and player.house_type == 'clay'
        success |= event_name == 'renovate' and player.house_type == 'stone'

        if success:
            player.add_resources(food=3)


class RoofBallaster(Occupation):
    deck = 'B'
    min_players = 1
    text = 'When you play this card, you can immediately pay 1 food total to receive 1 stone for each room you have.'

    def check_and_apply(self, player):
        use = player.game.get_choices(
            player,
            YesNoChoice(
                "RoofBallaster: pay 1 food total to receive "
                "1 stone for each room you have?"))

        if use:
            player.change_state(
                cost=dict(food=1),
                change=dict(stone=player.rooms))


class Tutor(Occupation):
    deck = 'B'
    min_players = 1
    text = 'During scoring, you get 1 bonus point for each occupation played after this one.'

    def victory_points(self, player):
        idx = player.occupations.index(self)
        return len(player.occupations) - idx - 1


class OvenFiringBoy(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use a wood accumulation space, you get an additional "Bake Bread" action.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: Grove')
        player.listen_for_event(self, 'Action: Copse')

    def trigger(self, player, **kwargs):
        grain = CountChoice(
            player.grain,
            "OvenFiringBoy: Number of grain bushels to bake into bread?")
        player.bake_bread(grain)


class OrganicFarmer(Occupation):
    deck = 'B'
    min_players = 1
    text = 'During the scoring, you get 1 bonus point for each pasture containing at least 1 animal while having unused capacity for at least 3 more animals.'

    def victory_points(self, player):
        pass


class Manservant(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Once you live in a stone house, place 3 food on each remaining round space. At the start of these rounds, you get the food.'

    def check_and_apply(self, player):
        if player.house_type == 'stone':
            player.add_future(range(1, 4), 'food', 1)
        else:
            player.listen_for_event(self, 'renovation')

    def trigger(self, player, **kwargs):
        if player.house_type == 'stone':
            player.add_future(range(1, 4), 'food', 1)
            player.stop_listening(self, 'renovation')


class AdoptiveParents(Occupation):
    deck = 'A'
    min_players = 1
    text = 'For 1 food, you can take an action with offspring in the same round you get it. If you do, the offspring does not count as "newborn".'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'birth')

    def trigger(self, player, **kwargs):
        #TODO
        pass


class Childless(Occupation):
    deck = 'B'
    min_players = 1
    text = 'At the start of each round, if you have at least 3 rooms but only 2 people, you get 1 food and 1 crop of your choice (grain or vegetable).'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.rooms >= 3 and player.people == 2:
            choice = DiscreteChoice(
                ["Grain", "Vegetable"],
                "Childless: Select type of seeds to receive.")
            seed_type = player.game.get_choices(player, [choice])
            if seed_type == choice.options[0]:
                player.add_resources(food=1, grain=1)
            elif seed_type == choice.options[1]:
                player.add_resources(food=1, veg=1)
            else:
                raise Exception()


class Geologist(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Each time you use the "Forest" or "Reed Bank" accumulation space, you also get 1 clay. In games with 3 or more players, this also applies to the "Clay Pit".'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: ReedBank')
        if player.game.n_players >= 3:
            player.listen_for_event(self, 'Action: ClayPit')

    def trigger(self, player, **kwargs):
        player.add_resources(clay=1)


class MushroomCollector(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Immediately after each time you use a wood accumulation space, you can exchange 1 wood for 2 food. If you do, place the wood on the accumulation space.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: Grove')
        player.listen_for_event(self, 'Action: Copse')

    def trigger(self, player, action):
        desc = "MushroomCollector; leave 1 wood to receive 2 food?"
        use = player.game.get_choice(player, YesNoChoice(desc))
        if use:
            player.change_state(
                "MushroomCollector effect.",
                cost=dict(wood=1),
                change=dict(food=2))


class Scholar(Occupation):
    deck = 'B'
    min_players = 1
    text = 'Once you live in a stone house, at the start of each round, you can play an occupation for an occupation cost of 1 food or a minor improvement (by paying its cost).'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.house_type == 'stone':
            choice = DiscreteChoice(
                ['Play occupation (at cost of 1 food).',
                 'Play minor improvement (at cost listed on card)',
                 'Do nothing'],
                "Scholar effect")
            action = player.game.get_choice(player, choice)

            if action == choice.options[0]:
                choice = DiscreteChoice(
                    player.hand['occupations'],
                    'Choose an occupation from your hand.')
                occ = player.game.get_choice(player, choice)
                player.play_occupation(occ, player.game)
            elif action == choice.options[0]:
                choice = DiscreteChoice(
                    player.hand["minor_improvements"],
                    "Choose a minor improvement to play.")
                imp = player.game.get_choice(player, choice)
                player.play_minor_improvement(imp, player.game)
            else:
                pass


class PlowDriver(Occupation):
    deck = 'A'
    min_players = 1
    text = 'Once you live in a stone house, at the start of each round, you can pay 1 food to plow 1 field.'

    def check_and_apply(self, player):
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.house_type == 'stone' and player.food >= 1:
            desc = "PlowDriver: Pay 1 food to plow a field?"
            use = player.game.get_choice(player, YesNoChoice(desc))
            if use:
                player.change_state("Plowdriver effect.", cost=dict(food=1))
                space_to_plow = player.game.get_choices(
                    player, SpaceChoice("Space to plow."))
                player.plow_fields(space_to_plow)


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

    def check_and_apply(self, player):
        player.house_progression['wood'].append('stone')


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

    def check_and_apply(self, player):
        if player.house_type == 'clay' and player.rooms == 2:
            player.add_resources(clay=3, reed=2, stone=2)


class MinorImprovement(with_metaclass(abc.ABCMeta, Card)):
    _victory_points = 0
    traveling = False

    def __init__(self):
        pass

    def check_and_apply(self, player):
        print("Applying minor improvement {0}.".format(self.name))
        description = "Playing minor improvement {0}".format(self)

        player.change_state(description, cost=self.cost.copy())
        self._check(player)
        self._apply(player)

    def _check(self, player):
        pass

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

    def _apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: Grove')
        player.listen_for_event(self, 'Action: Copse')

    def trigger(self, player, pasture):
        use = player.game.get_choices(player, YesNoChoice("Basket: exchange 2 wood for 3 food?"))
        if use:
            player.change_state("Basket effect.", cost=dict(wood=2), change=dict(food=3))


class ClayEmbankment(MinorImprovement):
    _cost = dict(food=1)
    deck = 'A'
    text = "You immediately get 1 clay for every 2 clay you already have in your supply."
    traveling = True

    def _apply(self, player):
        player.add_resources(clay=int(player.clay / 2))


class LargeGreenhouse(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'A'
    text = "Add 4, 7, and 9 to the current round and place 1 vegetable on each corresponding space. At the start of these rounds, you get that vegetable."

    def _check(self, player):
        return len(player.occupations) >= 2

    def _apply(self, player):
        player.add_future([4, 7, 9], 'veg', 1)


class SheperdsCrook(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = "Each time you fence a new pasture covering at least 4 farmyard spaces, you immediately get 2 sheep on this pasture."

    def _apply(self, player):
        player.listen_for_event(self, 'build_pasture')

    def trigger(self, player, pasture):
        if pasture.size >= 4:
            player.add_animals(sheep=2)


class Manger(MinorImprovement):
    _cost = dict(food=2)
    deck = 'A'
    text = "During scoring, if your pastures cover at least 6/7/8/10 farmyard spaces, you get 1/2/3/4 bonus points."

    def victory_points(self, player):
        n_pasture_spaces = len(set(self.pasture_spaces))
        return score_mapping(n_pasture_spaces, [6, 7, 8, 10], [0, 1, 2, 3, 4])


class Mantelpiece(MinorImprovement):
    _cost = dict(stone=1)
    deck = 'B'
    text = "When you play this card, you immediately get 1 bonus point for each complete round left to play. You may no longer renovate your house."

    def _check(self, player):
        return player.house_type in ['clay', 'stone']

    def _apply(self, player):
        self._rounds_remaining = player.game.rounds_remaining

    def victory_points(self, player):
        return self._rounds_remaining - 3


class HerringPot(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'B'
    text = 'Each time you use the "Fishing" accumulation space, place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'

    def _apply(self, player):
        player.listen_for_event(self, 'Action: Fishing')

    def trigger(self, player, **kwargs):
        player.add_future(range(1, 4), 'food', 1)


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

    def victory_points(self, player):
        return {'wood': 3, 'clay': 2, 'stone': 0}[player.house_type]


class Scullery(MinorImprovement):
    _cost = dict(wood=1, clay=1)
    deck = 'B'
    text = 'At the start of each round, if you live in a wooden house, you get 1 food.'

    def _apply(self, player):
        player.listen_for_event(self, 'start_round')

    def trigger(self, player, **kwargs):
        if player.house_type == 'wood':
            player.add_resources(food=1)


class Canoe(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'A'
    text = 'Each time you use the "Fishing" accumulation space, you get an additional 1 food and 1 reed.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 1

    def _apply(self, player):
        player.listen_for_event(self, 'Action: Fishing')

    def trigger(self, player, **kwargs):
        player.add_resources(food=1, reed=1)


class MiningHammer(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'When you play this card, you immediately get 1 food. Each time you renovate, you can also build a stable without paying wood.'

    def _apply(self, player):
        player.add_resources(food=1)
        player.listen_for_event(self, 'renovation')

    def trigger(self, player, **kwargs):
        use = player.game.get_choices("MiningHammer: build 1 stable for free?")
        if use:
            stable_loc = player.game.get_choices(player, SpaceChoice("Stable location."))
            player.build_stables(stable_loc, 0)


class BigCountry(MinorImprovement):
    _cost = dict()
    deck = 'A'
    text = 'For each complete round left to play, you immediately get 1 bonus point and 2 food.'

    def _check(self, player):
        return not player.empty_spaces

    def _apply(self, player):
        self._rounds_remaining = player.game.rounds_remaining
        player.add_resources(food=2*self._rounds_remaining)

    def victory_points(self, player):
        return self._rounds_remaining


class HardPorcelain(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'B'
    text = 'At any time, you can exchange 2/3/4 clay for 1/2/3 stone.'


class JunkRoom(MinorImprovement):
    _cost = dict(wood=1, clay=1)
    deck = 'A'
    text = 'Each time after you build an improvement, including this one, you get 1 food.'

    def _apply(self, player):
        player.listen_for_event(self, 'minor improvement')
        player.listen_for_event(self, 'major improvement')

    def trigger(self, player, **kwargs):
        player.add_resources(food=1)


class DrinkingTrough(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'Each of your pastures (with or without a stable) can hold up to 2 more animals.'

    def _apply(self, player):
        player.pasture_capacity_modifier += 2


class YoungAnimalMarket(MinorImprovement):
    _cost = dict(sheep=1)
    deck = 'A'
    text = 'You immediately get 1 cattle. (Effectively, you are exchanging 1 sheep for 1 cattle.)'
    traveling = True

    def _apply(self, player):
        player.add_animals(cattle=1)


class Caravan(MinorImprovement):
    _cost = dict(wood=3, food=3)
    deck = 'B'
    text = 'This card provides room for 1 person.'

    def _apply(self, player):
        player.room_for_people += 1


class Claypipe(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'In the returning home phase of each round, if you gained at least 7 building resources in the preceding work phase, you get 2 food.'

    def _apply(self, player):
        player.listen_for_event(self, 'return home')


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

    def _apply(self, player):
        player.listen_for_event(self, 'Action: DayLaborer')

    def trigger(self, player, **kwargs):
        player.add_resources(clay=3)


class ShiftingCultivation(MinorImprovement):
    _cost = dict(food=2)
    deck = 'A'
    text = 'Immediately plow 1 field.'
    traveling = True

    def _apply(self, player):
        space_to_plow = player.game.get_choices(player, SpaceChoice("Space to plow."))
        player.plow_fields(space_to_plow)


class PondHut(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) == 2

    def _apply(self, player):
        player.add_future(range(1, 4), 'food', 1)


class Loom(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'In the field phase of each harvest, if you have at least 1/4/7 sheep, you get 1/2/3 food. During scoring, you get 1 bonus point for every 3 sheep.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 2

    def _apply(self, player):
        player.listen_for_event(self, 'field phase')

    def trigger(self, player, **kwargs):
        food = score_mapping(player.sheep, [1, 4, 7], [0, 1, 2, 3])
        player.add_resources(food=food)

    def victory_points(self, player):
        return int(player.sheep / 3)


class MoldboardPlow(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 2 field tiles on this card. Twice this game, when you use the "Farmland" action space, you can also plow 1 field from this card.'

    def _check(self, player):
        return len(player.occupations) >= 1

    def _apply(self, player):
        self._fields_remaining = 2
        player.listen_for_event(self, 'Action: Farmland')

    def trigger(self, player, **kwargs):
        if self._fields_remaining > 0:
            use = player.game.get_choices(player, YesNoChoice("MoldboardPlow: plow an extra field?"))
            if use:
                self._fields_remaining -= 1
                space_to_plow = player.game.get_choices(player, SpaceChoice("Space to plow."))
                player.plow_fields(space_to_plow)


class MiniPasture(MinorImprovement):
    _cost = dict(food=2)
    deck = 'B'
    text = 'Immediately fence a farmyard space, without paying wood for the fences. (If you already have pastures, the new one must be adjacent to an existing one.)'
    traveling = True

    def _apply(self, player):

        space_to_pasteurize = player.game.get_choices(
            player, SpaceChoice("Space to pasteurize."))
        player.build_pasture([space_to_pasteurize])


class Pitchfork(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'Each time you use the "Grain Seeds" action space, if the "Farmland" action space is occupied, you also get 3 food.'

    def _apply(self, player):
        player.listen_for_event(self, 'Action: GrainSeeds')

    def trigger(self, player, **kwargs):
        for action in self.player.game.actions_taken:
            if action.name == "Farmland":
                player.add_resources(food=3)
                return


class Lasso(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'B'
    text = 'You can place exactly two people immediately after one another if at least one of them use the "Sheep Market", "Pig Market", or "Cattle Market" accumulation space.'

    def _apply(self, player):
        player.listen_for_event(self, 'Action: SheepMarket')
        player.listen_for_event(self, 'Action: BoarMarket')
        player.listen_for_event(self, 'Action: CattleMarket')

    def trigger(self, player, **kwargs):
        pass


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

    def _apply(self, player):
        player.listen_for_event(self, 'field phase')

    def trigger(self, player, **kwargs):
        if player.grain_fields >= 1 and player.veg_fields >= 1 and player.empty_fields >= 1:
            player.add_resources(food=3)


class MarketStall(MinorImprovement):
    _cost = dict(grain=1)
    deck = 'B'
    text = 'You immediately get 1 vegetable. (Effectively, you are exchanging 1 grain for 1 vegetable.)'
    traveling = True

    def _apply(self, player):
        player.add_resources(veg=1)


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

    def _apply(self, player):
        player.listen_for_event(self, 'field phase')

    def trigger(self, player, **kwargs):
        food = int(player.sheep/3) + int(player.cattle/3)
        player.add_resources(food=food)


class CarpentersParlor(MinorImprovement):
    _cost = dict(wood=1, stone=1)
    deck = 'B'
    text = 'Wooden rooms only cost you 2 wood and 2 reed each.'

    def _apply(self, player):
        # TODO
        player.listen_for_event(self, 'field phase')


class AcornBasket(MinorImprovement):
    _cost = dict(reed=1)
    deck = 'B'
    text = 'Place 1 wild boar on each of the next 2 round spaces. At the start of these rounds you get the wild boar.'

    def _check(self, player):
        return len(player.occupations) >= 3

    def _apply(self, player):
        player.add_future(range(1, 3), 'boar', 1)


class StrawberryPatch(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'Place 1 food on each of the next 3 round spaces. At the start of these rounds, you get the food.'
    _victory_points = 2

    def _check(self, player):
        return player.veg_fields >= 2

    def _apply(self, player):
        player.add_future(range(1, 4), 'food', 1)


class CornScoop(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use the "Grain Seeds" action space, you get 1 additional grain.'

    def _apply(self, player):
        player.listen_for_event(self, 'Action: GrainSeeds')

    def trigger(self, player, **kwargs):
        player.add_resources(grain=1)


class RammedClay(MinorImprovement):
    _cost = dict()
    deck = 'A'
    text = 'When you play this card, you immediately get 1 clay. You can use clay instead of wood to build fences.'

    def _apply(self, player):
        player.add_resources(clay=1)


class ThreshingBoard(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use the "Farmland", or "Cultivation" action space, you get an additional "Bake Bread" action.'
    _victory_points = 1

    def _check(self, player):
        return len(player.occupations) >= 2

    def _apply(self, player):
        player.listen_for_event(self, 'Action: Farmland')
        player.listen_for_event(self, 'Action: Cultivation')

    def trigger(self, player, **kwargs):
        grain = CountChoice(
            player.grain,
            "ThreshingBoard: Number of grain bushels to bake into bread?")
        player.bake_bread(grain)


class DutchWindmill(MinorImprovement):
    _cost = dict(wood=2, stone=2)
    deck = 'A'
    text = 'Each time you take a "Bake Bread" action in a round immediately following a harvest, you get 3 additional food.'
    _victory_points = 2

    def _apply(self, player):
        player.listen_for_event(self, 'bake bread')

    def trigger(self, player, **kwargs):
        sums = cumsum([len(s) for s in player.game.action_order[:1]])
        round_idx = player.game.round_idx
        for s in sums:
            if round_idx == s + 1:
                player.add_resources(food=3)


class StoneTongs(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Each time you use a stone accumulation space, you get 1 additional stone.'

    def _apply(self, player):
        player.listen_for_event(self, 'stone accumulation')

    def trigger(self, player, **kwargs):
        player.add_resources(stone=1)


class ThickForest(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 1 wood on each remaining even-numbered round space. At the start of these rounds, you get the wood.'

    def _check(self, player):
        return player.clay >= 5

    def _apply(self, player):
        n_rounds = len(player.game.action_order) - 1
        rounds = [r for r in range(player.game.round_idx+1, n_rounds+1) if r % 2 == 0]
        player.add_future(rounds, 'wood', 1, absolute=True)


class BreadPaddle(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'B'
    text = 'When you play this card, you immediately get 1 food. For each occupation you play, you get an additional "Bake Bread" action.'

    def _apply(self, player):
        player.add_resources(food=1)
        player.listen_for_event(self, 'occupation')

    def trigger(self, player, **kwargs):
        grain = CountChoice(
            player.grain,
            "BreadPaddle: Number of grain bushels to bake into bread?")
        player.bake_bread(grain)


class Handplow(MinorImprovement):
    _cost = dict(wood=1)
    deck = 'A'
    text = 'Add 5 to the current round and place 1 field tile on the corresponding round space. At the start of that round, you can plow the field.'

    def _apply(self, player):
        player.add_future([5], 'field', 1)


class MilkJug(MinorImprovement):
    _cost = dict(clay=1)
    deck = 'A'
    text = 'Each time any player (including you) uses the "Cattle Market" accumulation space, you get 3 food, and each other player gets 1 food.'

    def _apply(self, player):
        player.game.listen_for_event(self, 'Action: CattleMarket')
        self.player = player

    def trigger(self, player, **kwargs):
        for p in player.game.players:
            p.add_resources(food=1)
        self.player.add_resources(food=2)


class Brook(MinorImprovement):
    _cost = dict()
    deck = 'B'
    text = 'Each time you use one of the four action spaces above the "Fishing" accumulation space, you get 1 additional food.'

    def _check(self, player):
        # TODO: one of your people have to be on the fishing action space
        pass

    def _apply(self, player):
        player.listen_for_event(self, 'Action: Forest')
        player.listen_for_event(self, 'Action: ReedBank')
        player.listen_for_event(self, 'Action: ClayPit')
        action = player.game.action_order[1][0]
        player.listen_for_event(self, 'Action: {}'.format(action.name))

    def trigger(self, player, **kwargs):
        player.add_resources(food=1)


class SackCart(MinorImprovement):
    _cost = dict(wood=2)
    deck = 'B'
    text = 'Place 1 grain each on the remaining spaces for rounds 5, 8, 11, and 14. At the start of these rounds, you get the grain.'

    def _check(self, player):
        return len(player.occupations) >= 2

    def _apply(self, player):
        player.add_future([5, 8, 11, 14], 'grain', 1, absolute=True)


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


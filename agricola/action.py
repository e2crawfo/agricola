import abc
from future.utils import iteritems, with_metaclass

#from agricola import AgricolaInvalidChoice, AgricolaImpossible, AgricolaPoorlyFormed
from .errors import AgricolaInvalidChoice, AgricolaImpossible, AgricolaPoorlyFormed
from .choice import (
    DiscreteChoice, CountChoice, ListChoice,
    VariableLengthListChoice, SpaceChoice, MinorImprovementchoice)
from .cards import MinorImprovement as MinorImprovementCard
from .cards import MajorImprovement as MajorImprovementCard
from .player import Pasture
from . import const

class Action(with_metaclass(abc.ABCMeta, object)):
    choice_classes = []

    def __str__(self):
        return "<" + self.__class__.__name__ + ">"

    @property
    def name(self):
        return self.__class__.__name__

    def _check_choices(self, player, choices):
        pass

    # returns next required choice
    def choices(self, player, current_choices):
        index = 0
        choice_array = []
        for choice_class in self.choice_classes:
            if len(current_choices) <= index:
                return choice_array, choice_class
            choice = choice_class["class"](player, current_choices[index])
            choice_array.append(choice)
            index += 1
            while not choice.next_choices == None and \
                  not len(choice.next_choices) == 0:
                for next_choice in choice.next_choices:
                    print("next_choice")
                    print(next_choice)
                    if len(current_choices) <= index:
                        return choice_array, next_choice
                    print(current_choices[index])
                    choice = next_choice["class"](player, current_choices[index]) 
                    choice_array.append(choice)
                    index += 1

        return choice_array, None

    def effect_with_dict(self, player, action_dict):
        choices = self._convert_action_dict(player, action_dict)
        self._effect(player, choices)

    def effect(self, player, choices):
        self._check_choices(player, choices)
        self._effect(player, choices)

    @abc.abstractmethod
    def _effect(self, player, choices):
        pass

    def _convert_action_dict(self, player, action_dict):
        return []

    def get_id(self):
        return self.__class__.__name__

    def get_state_dict(self):
        return {
            "action_id": self.get_id()
        }

    def turn(self):
        # Called at the beginning of every round.
        pass


class ResourceAcquisition(Action):
    resources = {}

    def __str__(self):
        s = ["<" + self.__class__.__name__ + ":"]

        pairs = list(self.resources.items())
        for k, v in pairs[:-1]:
            s.append("+{0} {1},".format(v, k))
        s.append("+{0} {1}".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s) + '>'

    def _effect(self, player, choices):
        for resource, amount in iteritems(self.resources):
            setattr(player, resource, getattr(player, resource) + amount)


class Accumulating(ResourceAcquisition):
    acc_amount = {}

    def __init__(self):
        self.resources = {}
        for k, v in iteritems(self.acc_amount):
            self.resources[k] = 0

    def __str__(self):
        s = ["<" + self.__class__.__name__ + ":"]

        pairs = list(iteritems(self.resources))
        n_pairs = len(pairs)

        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1}".format(pairs[-1][1], pairs[-1][0]))

        pairs = list(iteritems(self.acc_amount))
        n_pairs = len(pairs)

        s.append("(replenishes")
        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1})".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s) + '>'

    def _effect(self, player, choices):
        super(Accumulating, self)._effect(player, choices)
        for resource in self.acc_amount:
            self.resources[resource] = 0

    def turn(self):
        for resource, amount in iteritems(self.acc_amount):
            self.resources[resource] += amount

    def get_state_dict(self):
        pairs = list(iteritems(self.resources))
        state_resources = []

        for i, (k, v) in enumerate(pairs):
            state_resources.append({
                "resource_type": k,
                "resource_amount": v
            })

        return {
            "action_id": self.get_id(),
            "resources": state_resources
        }

class BasicWishForChildren(Action):
    def choices(self, player):
        return [
            DiscreteChoice(
               player.hand['minor_improvements'],
               "Pick an optional minor improvement after childbirth.")
        ]

    def _effect(self, player, choices):
        player.add_people(1)
        if choices[0] is not None:
            player.play_minor_improvement(choices[0], player.game)

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["improvement"]["id"]]

class ModestWishForChildren(Action):
    def _effect(self, player, choices):
        if player.game.round_idx < 5:
            raise AgricolaImpossible(
                "ModestWishForChildren action can only been chosen in "
                "round 5 or later.")

        player.add_people(1)


class UrgentWishForChildren(Action):
    def _effect(self, player, choices):
        player.add_people(1)


class DayLaborer(ResourceAcquisition):
    resources = dict(food=2)


class Fishing(Accumulating):
    acc_amount = dict(food=1)

class TravelingPlayers(Fishing):
    pass

class Copse(Accumulating):
    acc_amount = dict(wood=1)


class Grove(Accumulating):
    acc_amount = dict(wood=2)


class Forest(Accumulating):
    acc_amount = dict(wood=3)


# class LargeForest(Accumulating):
#     acc_amount = dict(wood=4)


class ClayPit(Accumulating):
    acc_amount = dict(clay=1)


class Hollow3P(Accumulating):
    acc_amount = dict(clay=1)


class Hollow4P(Accumulating):
    acc_amount = dict(clay=2)


#class Hollow5P(Accumulating):
#    acc_amount = dict(clay=3)


class EasternQuarry(Accumulating):
    acc_amount = dict(stone=1)


class WesternQuarry(EasternQuarry):
    pass

class ResourceMarket2P(ResourceAcquisition):
    resources = dict(food=1, stone=1)


class ResourceMarket3P(ResourceAcquisition):
    resources = dict(food=1)

    def choices(self, player):
        return [
            DiscreteChoice(["reed", "stone"], "Choose between 1 reed/1 stone.")
        ]

    def _effect(self, player, choices):
        reed = choices[0] == 'reed'
        stone = choices[0] == 'stone'

        if not reed and not stone:
            raise AgricolaInvalidChoice()

        resources = self.resources.copy()
        resources[choices[0]] = 1
        resources["food"] = 1
        player.add_resources(resources)

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["resource_type"]]


class ResourceMarket4P(ResourceAcquisition):
    resources = dict(food=1, stone=1, reed=1)

class ReedBank(Accumulating):
    acc_amount = dict(reed=1)


class SheepMarket(Accumulating):
    acc_amount = dict(sheep=1)


class PigMarket(Accumulating):
    acc_amount = dict(boar=1)


class CattleMarket(Accumulating):
    acc_amount = dict(cattle=1)

class AnimalMarket(ResourceAcquisition):
    resources = dict()

    def choices(self, player):
        return [
            DiscreteChoice(["sheep", "boar", "cattle"],
                           "Choose between 1 sheep, 1 food/1 boar/1 cattle, -1 food.")
        ]

    def _effect(self, player, choices):
        if choices[0] == "sheep":
            player.add_resources(food=1)
            player.add_animals(sheep=1)
        elif choices[0] == "boar":
            player.add_animals(boar=1)
        elif choices[0] == "cattle":
            player.add_resources(food=-1)
            player.add_animals(cattle=1)
        else:
            raise AgricolaInvalidChoice()

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["animal_type"]]

class FarmExpansion(Action):
    def choices(self, player):
        return [
            VariableLengthListChoice(SpaceChoice("Room location."), "Number of rooms."),
            VariableLengthListChoice(SpaceChoice("Stable location."), "Number of stables.")
        ]

    def _effect(self, player, choices):
        if not isinstance(choices[0], list) and not isinstance(choices[1], list):
            raise AgricolaInvalidChoice(
                "At least one of the two actions (build rooms or build stables) "
                "must be selected to use this action space.")

        room_spaces = choices[0]
        if room_spaces is None:
            pass
        elif isinstance(room_spaces, list):
            player.build_rooms(room_spaces)
        else:
            raise AgricolaInvalidChoice(
                "Rooms have to be specified as a list of spaces.")

        stable_spaces = choices[1]
        if stable_spaces is None:
            pass
        elif isinstance(stable_spaces, list):
            player.build_stables(stable_spaces, 2)
        else:
            raise AgricolaInvalidChoice(
                "Stables have to be specified as a list of spaces.")

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["rooms"], action_dict["stables"]]

    

class HouseRedevelopment(Action):
    def choices(self, player):
        house_upgrade_mats = player.valid_house_upgrades()
        imps = player.hand["minor_improvements"] + player.game.major_improvements
        return [
            DiscreteChoice(house_upgrade_mats, "Choose new house material."),
            DiscreteChoice(imps, "Choose an optional improvement after renovation.")]

    def _effect(self, player, choices):
        player.upgrade_house(choices[0])

        imp = choices[1]
        if imp is not None:
            if isinstance(imp, MinorImprovementCard):
                player.play_minor_improvement(imp, player.game)
            elif isinstance(imp, MajorImprovementCard):
                player.play_major_improvement(imp, player.game)
                player.game.major_improvements.remove(imp)
            else:
                raise AgricolaPoorlyFormed(
                    "Received {0}, but a major/minor improvement was expected.")
    
    def _convert_action_dict(self, player, action_dict):
        return [action_dict["material"], action_dict["improvement"]["id"]]

class FarmRedevelopment(Action):
    def choices(self, player):
        return [
            DiscreteChoice(player.house_progression[player.house_type], "Choose new house material."),
            ListChoice(ListChoice(SpaceChoice("Space to pasteurize.")))
        ]

    def _effect(self, player, choices):
        player.upgrade_house(choices[0])
        if choices[1] is not None:
            player.build_pastures(choices[1])

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["material"], action_dict["pastures"]]


class MajorImprovement(Action):
    def choices(self, player):
        imps = player.hand["minor_improvements"] + player.game.major_improvements
        return [
            DiscreteChoice(imps, "Choose a major or minor improvement.")
        ]

    def _effect(self, player, choices):
        imp = choices[0]
        if isinstance(imp, MinorImprovementCard):
            player.play_minor_improvement(imp, player.game)
        elif isinstance(imp, MajorImprovementCard):
            player.play_major_improvement(imp, player.game)
            player.game.major_improvements.remove(imp)
        else:
            raise AgricolaPoorlyFormed(
                "Received {0}, but a major/minor improvement was expected.")

    def _convert_action_dict(self, player, action_dict):
        # TODO read additional props when needed ex: field
        return [action_dict["id"]]

class Fencing(Action):
    def choices(self, player):
        return [
            VariableLengthListChoice(
                VariableLengthListChoice(SpaceChoice("Space to pasteurize.")))
        ]

    def _effect(self, player, choices):
        pastures = choices[0]
        if pastures is None:
            pass
        elif isinstance(pastures, list):
            player.build_pastures(pastures)
        else:
            raise AgricolaInvalidChoice(
                "Pastures have to be specified as a list of list of spaces.")

    def _convert_action_dict(self, player, action_dict):
        pasture_array = list(map(lambda p_array: Pasture(list(map(lambda pasture: (pasture[1], pasture[0]) ,p_array))), action_dict["pastures"]))
        return [pasture_array]

class Lessons(Action):
    def choices(self, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, player, choices):
        if len(player.occupations) > 0:
            player.change_state("Playing occupation", cost=dict(food=1))

        player.play_occupation(choices[0], player.game)

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["occupation_id"]]

class Lessons3P(Action):
    def choices(self, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, player, choices):
        player.change_state("Playing occupation", cost=dict(food=2))
        player.play_occupation(choices[0], player.game)

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["occupation_id"]]

class Lessons4P(Action):
    def choices(self, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, player, choices):
        if len(player.occupations) > 1:
            player.change_state("Playing occupation", cost=dict(food=2))
        else:
            player.change_state("Playing occupation", cost=dict(food=1))

        player.play_occupation(choices[0], player.game)

    def _convert_action_dict(self, player, action_dict):
        return [action_dict["occupation_id"]]


# class Lessons5P(Action):
#     def choices(self, player):
#         return [
#             DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
#         ]

#     def _effect(self, player, choices):
#         if len(player.occupations) > 0:
#             player.change_state("Playing occupation", cost=dict(food=1))
#         else:
#             player.change_state("Playing occupation", cost=dict(food=0))

#         player.play_occupation(choices[0], player.game)


class MeetingPlace(Action):
    choice_classes = [{
        "class": MinorImprovementchoice,
        "source": ""
    }]

    def _effect(self, player, choices):
        player.game.set_first_player(int(player.name))
        if choices[0].choice_value is not None:
            player.play_minor_improvement(choices[0].choice_value, choices[1:], player.game)

    def _convert_action_dict(self, player, action_dict):
        if "improvement" in action_dict:
            return [action_dict["improvement"]["id"]]
        return [None]

class MeetingPlaceFamily(Accumulating):
    acc_amount = dict(food=1)

    def _effect(self, player, choices):
        player.game.set_first_player(player)
        super(MeetingPlaceFamily, self)._effect(player, choices)

    def _convert_action_dict(self, player, action_dict):
        return [(action_dict["ploughing_space"][1], action_dict["ploughing_space"][0])]


class Farmland(Action):
    choice_classes = [{
        "class": SpaceChoice,
        "source": const.event_sources.plough
    }]

    def _effect(self, player, choices):
        player.plow_fields(choices[0].choice_value)

class Cultivation(Action):
    def choices(self, player):
        return [
            SpaceChoice("Space to plow."),
            CountChoice(player.grain, "Number of grain seeds to plant."),
            CountChoice(player.veg, "Number of vegatable seeds to plant.")]

    def _effect(self, player, choices):
        if all(i is None for i in choices):
            raise AgricolaInvalidChoice(
                "Must perform at least one of: plow field, sow.")

        if choices[0] is not None:
            player.plow_fields(choices[0])

        if choices[1] is not None or choices[2] is not None:
            grain = choices[1] or 0
            veg = choices[2] or 0
            player.sow(grain, veg)

    def _convert_action_dict(self, player, action_dict):
        # TODO choose grain plant field
        # TODO choose vegitable plant field
        return [(action_dict["ploughing_space"][0], action_dict["ploughing_space"][1]), action_dict["plant_grain_count"], action_dict["plant_vegitable_count"]]


class GrainUtilization(Action):
    def choices(self, player):
        return [
            CountChoice(player.grain, "Number of grain seeds to plant."),
            CountChoice(player.veg, "Number of vegatable seeds to plant."),
            CountChoice(player.grain, "Number of grain bushels to bake into bread.")]

    def _effect(self, player, choices):
        if all(i is None for i in choices):
            raise AgricolaInvalidChoice("Must perform at least one of: sow, bake bread.")

        if choices[0] is not None or choices[1] is not None:
            grain = choices[0] or 0
            veg = choices[1] or 0
            player.sow(grain, veg)

        if choices[2] is not None:
            player.bake_bread(choices[2])

    def _convert_action_dict(self, player, action_dict):
        # TODO choose grain plant field
        # TODO choose vegitable plant field
        # TODO choose baking improvement
        return [action_dict["plant_grain_count"], action_dict["plant_vegitable_count"], action_dict["bake_grain_count"]]



class GrainSeeds(ResourceAcquisition):
    resources = dict(grain=1)


class VegetableSeeds(ResourceAcquisition):
    resources = dict(veg=1)

class SideJob(Action):
    def choices(self, player):
        return [
            SpaceChoice("Stable location."),
            CountChoice(player.grain, "Number of grain bushels to bake into bread.")]

    def _effect(self, player, choices):
        if all(i is None for i in choices):
            raise AgricolaInvalidChoice(
                "Must perform at least one of: build stable, bake bread.")

        if choices[0] is not None:
            player.build_stables(choices[0], 1)

        if choices[1] is not None:
            player.bake_bread(choices[1])


class CompoundAction(Action):
    pass


def get_simple_actions(family=True):
    meeting_place = MeetingPlaceFamily() if family else MeetingPlace()
    actions = [
        [meeting_place, GrainSeeds(), DayLaborer(), Forest(), ClayPit(),
         ReedBank(), Fishing()],
        [SheepMarket()],
        [WesternQuarry()],
        [VegetableSeeds(), PigMarket()],
        [CattleMarket(), EasternQuarry()],
        [UrgentWishForChildren()]]

    return actions


def core_actions(family):
    meeting_place = MeetingPlaceFamily() if family else MeetingPlace()
    actions = [
        [FarmExpansion(), meeting_place, GrainSeeds(), Farmland(),
         DayLaborer(), Forest(), ClayPit(), ReedBank(), Fishing()],
        [MajorImprovement(), SheepMarket(), Fencing(), GrainUtilization()],
        [BasicWishForChildren(), HouseRedevelopment(), WesternQuarry()],
        [VegetableSeeds(), PigMarket()],
        [CattleMarket(), EasternQuarry()],
        [Cultivation(), UrgentWishForChildren()],
        [FarmRedevelopment()]]
    if family:
        actions[0].append(SideJob())
    else:
        actions[0].append(Lessons())

    return actions


def get_actions(family, n_players):
    actions = core_actions(family)

    if n_players == 2 or n_players == 1:
        pass
    elif n_players == 3:
        actions[0].extend([
            Grove(), ResourceMarket3P(), Hollow3P(), Lessons3P()])
    elif n_players == 4:
        actions[0].extend([
            Copse(), Grove(), ResourceMarket4P(), Hollow4P(),
            Lessons4P(), TravelingPlayers()])
    # elif n_players == 5:
    #     actions[0].extend([
    #         Copse(), Grove(), ResourceMarket4P(), Hollow5P(), Hollow3P(),
    #         Lessons5P(), TravelingPlayers()])
    else:
        raise NotImplementedError(
            "Do not know how to play a player.game with {0} players.".format(n_players))
    return actions

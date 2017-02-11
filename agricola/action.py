import abc
from future.utils import iteritems, with_metaclass

from agricola import AgricolaInvalidChoice, AgricolaImpossible, AgricolaPoorlyFormed
from agricola.cards import MinorImprovement as MinorImprovementCard
from agricola.cards import MajorImprovement as MajorImprovementCard


class Choice(object):
    def __init__(self, desc=None):
        self.desc = desc

    def validate(self, choice):
        pass


class DiscreteChoice(Choice):
    def __init__(self, options, desc=None):
        if not options:
            raise ValueError(
                "Cannot create a DiscreteChoice instance with an empty "
                "options list. Choice description is:\n{0}".format(desc))

        super(DiscreteChoice, self).__init__(desc)
        self.options = list(options)


class CountChoice(Choice):
    def __init__(self, n=None, desc=None):
        self.n = n
        super(CountChoice, self).__init__(desc)


class ListChoice(Choice):
    def __init__(self, subchoices, desc=None):
        super(ListChoice, self).__init__(desc)
        self.subchoices = subchoices


class VariableLengthListChoice(Choice):
    def __init__(self, subchoice, desc=None):
        super(VariableLengthListChoice, self).__init__(desc)
        self.subchoice = subchoice


class SpaceChoice(Choice):
    def __init__(self, desc=None):
        super(SpaceChoice, self).__init__(desc)


class Action(with_metaclass(abc.ABCMeta, object)):
    def __str__(self):
        return "<" + self.__class__.__name__ + ">"

    def _check_choices(self, game, player, choices):
        _choices = self.choices(game, player)
        if len(choices) != len(_choices):
            raise AgricolaInvalidChoice(
                "Expected {0} choices, but received {1} choices.".format(
                    len(_choices), len(choices)))

    def choices(self, game, player):
        return []

    def effect(self, game, player, choices):
        self._check_choices(game, player, choices)
        self._effect(game, player, choices)

    @abc.abstractmethod
    def _effect(self, game, player, choices):
        pass

    def turn(self):
        # Called at the beginning of every round.
        pass


class ResourceAcquisition(Action):
    resources = {}

    def __str__(self):
        s = ["<" + self.__class__.__name__ + ":"]

        pairs = list(iteritems(self.resources))
        n_pairs = len(pairs)

        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1}".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s) + '>'

    def _effect(self, game, player, choices):
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

    def _effect(self, game, player, choices):
        super(Accumulating, self)._effect(game, player, choices)
        for resource in self.acc_amount:
            self.resources[resource] = 0

    def turn(self):
        for resource, amount in iteritems(self.acc_amount):
            self.resources[resource] += amount


class BasicWishForChildren(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(
               player.hand['minor_improvements'],
               "Pick an optional minor improvement after childbirth.")
        ]

    def _effect(self, game, player, choices):
        player.add_people(1)
        if choices[0] is not None:
            player.play_minor_improvement(choices[0], game)


class ModestWishForChildren(Action):
    def _effect(self, game, player, choices):
        if game.round_idx < 5:
            raise AgricolaImpossible(
                "ModestWishForChildren action can only been chosen in "
                "round 5 or later.")

        player.add_people(1)


class UrgentWishForChildren(Action):
    def _effect(self, game, player, choices):
        player.add_people(1)


class DayLaborer(ResourceAcquisition):
    resources = dict(food=2)


class Fishing(Accumulating):
    acc_amount = dict(food=1)


class TravellingPlayers(Fishing):
    pass


class Copse(Accumulating):
    acc_amount = dict(wood=1)


class Grove(Accumulating):
    acc_amount = dict(wood=2)


class Forest(Accumulating):
    acc_amount = dict(wood=3)


class ClayPit(Accumulating):
    acc_amount = dict(clay=1)


class Hollow3P(Accumulating):
    acc_amount = dict(clay=1)


class Hollow4P(Accumulating):
    acc_amount = dict(clay=2)


class EasternQuarry(Accumulating):
    acc_amount = dict(stone=1)


class WesternQuarry(EasternQuarry):
    pass


class ResourceMarket2P(ResourceAcquisition):
    resources = dict(food=1, stone=1)


class ResourceMarket3P(ResourceAcquisition):
    resources = dict(food=1)

    def choices(self, game, player):
        return [
            DiscreteChoice(["reed", "stone"], "Choose between 1 reed/1 stone.")
        ]

    def _effect(self, game, player, choices):
        reed = choices[0] == 'reed'
        stone = choices[0] == 'stone'

        if not reed and not stone:
            raise AgricolaInvalidChoice()

        resources = self.resources.copy()
        resources[choices[0]] = 1
        resources["food"] = 1
        player.add_resources(resources)


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

    def choices(self, game, player):
        return [
            DiscreteChoice(["sheep", "boar", "cattle"],
                           "Choose between 1 sheep, 1 food/1 boar/1 cattle, -1 food.")
        ]

    def _effect(self, game, player, choices):
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


class FarmExpansion(Action):
    def choices(self, game, player):
        return [
            VariableLengthListChoice(SpaceChoice("Room location.")),
            VariableLengthListChoice(SpaceChoice("Stable location."))
        ]

    def _effect(self, game, player, choices):
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


class HouseRedevelopment(Action):
    def choices(self, game, player):
        imps = player.hand["minor_improvements"] + game.major_improvements
        return [
            DiscreteChoice(["clay", "stone"], "Choose new house material."),
            DiscreteChoice(imps, "Choose an optional improvement after renovation.")]

    def _effect(self, game, player, choices):
        player.upgrade_house(choices[0])

        imp = choices[1]
        if imp is not None:
            if isinstance(imp, MinorImprovementCard):
                player.play_minor_improvement(imp, game)
            elif isinstance(imp, MajorImprovementCard):
                player.play_major_improvement(imp, game)
                game.major_improvements.remove(imp)
            else:
                raise AgricolaPoorlyFormed(
                    "Received {0}, but a major/minor improvement was expected.")


class FarmRedevelopment(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(["clay", "stone"], "Choose new house material."),
            ListChoice(ListChoice(SpaceChoice("Space to pasteurize.")))
        ]

    def _effect(self, game, player, choices):
        player.upgrade_house(choices[0])
        if choices[1] is not None:
            player.build_pastures(choices[1])


class MajorImprovement(Action):
    def choices(self, game, player):
        imps = player.hand["minor_improvements"] + game.major_improvements
        return [
            DiscreteChoice(imps, "Choose a major or minor improvement.")
        ]

    def _effect(self, game, player, choices):
        imp = choices[0]
        if isinstance(imp, MinorImprovementCard):
            player.play_minor_improvement(imp, game)
        elif isinstance(imp, MajorImprovementCard):
            player.play_major_improvement(imp, game)
            game.major_improvements.remove(imp)
        else:
            raise AgricolaPoorlyFormed(
                "Received {0}, but a major/minor improvement was expected.")


class Fencing(Action):
    def choices(self, game, player):
        return [
            VariableLengthListChoice(
                VariableLengthListChoice(SpaceChoice("Space to pasteurize.")))
        ]

    def _effect(self, game, player, choices):
        pastures = choices[0]
        if pastures is None:
            pass
        elif isinstance(pastures, list):
            player.build_pastures(pastures)
        else:
            raise AgricolaInvalidChoice(
                "Pastures have to be specified as a list of list of spaces.")


class Lessons(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, game, player, choices):
        if len(player.occupations) > 0:
            player.change_state("Playing occupation", change={'food': -1})

        player.play_occupation(choices[0], game)


class Lessons3P(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, game, player, choices):
        player.change_state("Playing occupation", change={'food': -2})
        player.play_occupation(choices[0], game)


class Lessons4P(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(player.hand['occupations'], 'Choose an occupation from your hand.')
        ]

    def _effect(self, game, player, choices):
        if len(player.occupations) > 1:
            player.change_state("Playing occupation", change={'food': -2})
        else:
            player.change_state("Playing occupation", change={'food': -1})

        player.play_occupation(choices[0], game)


class MeetingPlace(Action):
    def choices(self, game, player):
        return [
            DiscreteChoice(
               player.hand['minor_improvements'], "Choose an optional minor improvement.")
        ]

    def _effect(self, game, player, choices):
        game.set_first_player(player)
        if choices[0] is not None:
            player.play_minor_improvement(choices[0], game)


class MeetingPlaceFamily(Accumulating):
    acc_amount = dict(food=1)

    def _effect(self, game, player, choices):
        game.set_first_player(player)
        super(MeetingPlaceFamily, self)._effect(game, player, choices)


class Farmland(Action):
    def choices(self, game, player):
        return [SpaceChoice("Space to plow.")]

    def _effect(self, game, player, choices):
        player.plow_fields(choices[0])


class Cultivation(Action):
    def choices(self, game, player):
        return [
            SpaceChoice("Space to plow."),
            CountChoice(player.grain, "Number of grain seeds to plant."),
            CountChoice(player.veg, "Number of vegatable seeds to plant.")]

    def _effect(self, game, player, choices):
        if all(i is None for i in choices):
            raise AgricolaInvalidChoice(
                "Must perform at least one of: plow field, sow.")

        if choices[0] is not None:
            player.plow_fields(choices[0])

        if choices[1] is not None or choices[2] is not None:
            grain = choices[1] or 0
            veg = choices[2] or 0
            player.sow(grain, veg)


class GrainUtilization(Action):
    def choices(self, game, player):
        return [
            CountChoice(player.grain, "Number of grain seeds to plant."),
            CountChoice(player.veg, "Number of vegatable seeds to plant."),
            CountChoice(player.grain, "Number of grain bushels to bake into bread.")]

    def _effect(self, game, player, choices):
        if all(i is None for i in choices):
            raise AgricolaInvalidChoice("Must perform at least one of: sow, bake bread.")

        if choices[0] is not None or choices[1] is not None:
            grain = choices[0] or 0
            veg = choices[1] or 0
            player.sow(grain, veg)

        if choices[2] is not None:
            player.bake_bread(choices[2])


class GrainSeeds(ResourceAcquisition):
    resources = dict(grain=1)


class VegetableSeeds(ResourceAcquisition):
    resources = dict(veg=1)


class SideJob(Action):
    def choices(self, game, player):
        return [
            SpaceChoice("Stable location."),
            CountChoice(player.grain, "Number of grain bushels to bake into bread.")]

    def _effect(self, game, player, choices):
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

    if n_players == 2:
        pass
    elif n_players == 3:
        actions[0].extend([
            Grove(), ResourceMarket3P(), Hollow3P(), Lessons3P()])
    elif n_players == 4:
        actions[0].extend([
            Copse(), Grove(), ResourceMarket4P(), Hollow4P(),
            Lessons4P(), TravellingPlayers()])
    else:
        raise NotImplementedError(
            "Do not know how to play a game with {0} players.".format(n_players))
    return actions

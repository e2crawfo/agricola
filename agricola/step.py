import abc
import itertools
from future.utils import with_metaclass
from .choice import (ActionChoice, MinorImprovementChoice, SpaceChoice, OccupationChoice)
from . import const

class Step(with_metaclass(abc.ABCMeta, object)):
    def __init__(self):
        pass

    def get_required_choice_and_source(self):
        return None, None

    # returns next stack items
    def effect(self, game, player, choice):
        return None

class ActionSelectionStep(Step):
    def get_required_choice_and_source(self):
        return ActionChoice, const.event_sources.game

    def effect(self, game, player, choise):
        game.actions_taken[choise.choice_value] = player.index
        game.actions_remaining.remove(choise.choice_value)
        game.players[player.index].turn_left -= 1
        return choise.choice_value.effect(player)
        
class PlayOccupationStep(Step):
    def get_required_choice_and_source(self):
        # TODO set proper source
        return OccupationChoice, "occupation"

    def effect(self, game, player, choice):
        player.play_occupation(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

class PlayMajorImprovementStep(Step):
    pass

class PlayMinorImprovementStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return MinorImprovementChoice, "minor_improvement"

    def effect(self, game, player, choice):
        player.play_minor_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

class ResourcePayingStep(Step):
    pass

class RenovatingStep(Step):
    pass

class PlowingStep(Step):

    def get_required_choice_and_source(self):
        # TODO set source
        return SpaceChoice, "plowing"

    def effect(self, game, player, choice):
        player.plow_fields(choice.choice_value)

class HouseBuildingStep(Step):
    pass

class StableBuildingStep(Step):
    pass

class SowingStep(Step):
    pass

class BakingStep(Step):
    pass

class FencingStep(Step):
    pass

class AnimalMarketStep(Step):
    pass
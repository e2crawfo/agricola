import abc
import itertools
from future.utils import with_metaclass
from .choice import (ActionChoice, MinorImprovementChoice, SpaceChoice, OccupationChoice, FencingChoice, MajorImprovementChoice)
from . import const, cards

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

    def effect(self, game, player, choice):
        game.actions_taken[choice.choice_value] = player.index
        game.actions_remaining.remove(choice.choice_value)
        game.players[player.index].turn_left -= 1
        return choice.choice_value.effect(player)

class PlayOccupationStep(Step):
    def get_required_choice_and_source(self):
        # TODO set proper source
        return OccupationChoice, "occupation"

    def effect(self, game, player, choice):
        player.play_occupation(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

class PlayMajorImprovementStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return MajorImprovementChoice, "major_improvement"

    def effect(self, game, player, choice):
        if not choice.choice_value:
            return
        if isinstance(choice.choice_value, cards.MinorImprovement):
            player.play_minor_improvement(choice.choice_value, game)
        if isinstance(choice.choice_value, cards.MajorImprovement):
            player.play_major_improvement(choice.choice_value, game)
        
        return choice.choice_value.check_and_apply(player)

class PlayMinorImprovementStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return MinorImprovementChoice, "minor_improvement"

    def effect(self, game, player, choice):
        player.play_minor_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

# class ResourcePayingStep(Step):
#     pass

class RenovatingStep(Step):
    pass

class PlowingStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return PlowingChoice, "plowing"

    def effect(self, game, player, choice):
        player.plow_fields(choice.choice_value)

class HouseBuildingStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return HouseBuildingChoice, "room_building"
    
    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_rooms(choice.choice_value)
            return [HouseBuildingStep()]

class StableBuildingStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return StableBuildingChoice, "stable_building"
    
    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_stables(choice.choice_value, 2)
            return [StableBuildingStep()]

class SowingStep(Step):
    pass

class BakingStep(Step):
    pass

class FencingStep(Step):
    def get_required_choice_and_source(self):
        # TODO set source
        return FencingChoice, "fencing"
    
    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_pastures(choice.choice_value)

class AnimalMarketStep(Step):
    pass

import abc
import itertools
from future.utils import with_metaclass
from .choice import (ActionChoice, MinorImprovementChoice, SpaceChoice, OccupationChoice, FencingChoice, MajorImprovementChoice, PlowingChoice, StableBuildingChoice, HouseBuildingChoice, ResourceTradingChoice)
from . import const, cards
from .utils import dotDict, recDotDefaultDict
from collections import defaultdict

class Step(with_metaclass(abc.ABCMeta, object)):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_required_choice(self, game, player):
        pass

    # returns next stack items
    def effect(self, game, player, choice):
        return None

class ActionSelectionStep(Step):
    def get_required_choice(self, game, player):
        return ActionChoice(game, player)

    def effect(self, game, player, choice):
        game.actions_taken[choice.choice_value] = player.index
        game.actions_remaining.remove(choice.choice_value)
        game.players[player.index].turn_left -= 1
        return choice.choice_value.effect(player)

class PlayOccupationStep(Step):
    def get_required_choice(self, game, player):
        # TODO set proper source
        return OccupationChoice(game, player)

    def effect(self, game, player, choice):
        player.play_occupation(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

class PlayMajorImprovementStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return MajorImprovementChoice(game, player)

    def effect(self, game, player, choice):
        if not choice.choice_value:
            return
        if isinstance(choice.choice_value, cards.MinorImprovement):
            player.play_minor_improvement(choice.choice_value, game)
        if isinstance(choice.choice_value, cards.MajorImprovement):
            player.play_major_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

class PlayMinorImprovementStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return MinorImprovementChoice(game, player)

    def effect(self, game, player, choice):
        player.play_minor_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(player)

# class ResourcePayingStep(Step):
#     pass

class TakingResourcesFromActionStep(Step):
  def __init__(self, resources):
    self.resources = resources.copy()
    # self.resource_choices = [({'action_resources': self.resources, 
    #                            'additional_resources': defaultdict(int)})]
    # # TODO check occupation and improvements
    # resource_choice_filters = player.trigger_event(const.trigger_event_names.take_resources_from_action, player, resource_choices=self.resource_choices)

    # # TODO think about junretu
    # for resource_choice_filter in resource_choice_filters:
    #   self.resource_choices = resource_choice_filter(self.resource_choices)

  def get_required_choice(self, game, player):
    # TODO trigger event
    return ResourceTradingChoice(game, player, self.resources)

  def effect(self, game, player, choice):
    # # TODO use choice
    # if len(self.resource_choices) == 1:
    #   change = self.resource_choices[0]["action_resources"]
    #   for k, v in self.resource_choices[0]["additional_resources"].items():
    #     change[k] += v
    # player.change_state("", change=change)
    selected_candidate = choice.summarized_candidates[choice.selected_candidate_idx]
    player.change_state("", change=selected_candidate)
    

class RenovatingStep(Step):
    pass

class PlowingStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return PlowingChoice(game, player)

    def effect(self, game, player, choice):
        player.plow_fields(choice.choice_value)

class HouseBuildingStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return HouseBuildingChoice(game, player)
    
    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_rooms(choice.choice_value)
            return [HouseBuildingStep()]

class StableBuildingStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return StableBuildingChoice(game, player)

    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_stables(choice.choice_value, 2)
            return [StableBuildingStep()]

class SowingStep(Step):
    pass

class BakingStep(Step):
    pass

class FencingStep(Step):
    def get_required_choice(self, game, player):
        # TODO set source
        return FencingChoice(game, player)
    
    def effect(self, game, player, choice):
        if choice.choice_value:
            player.build_pastures(choice.choice_value)

class AnimalMarketStep(Step):
    pass

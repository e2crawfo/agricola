import abc
import itertools
from future.utils import with_metaclass
from .choice import (ActionChoice, MinorImprovementChoice, SpaceChoice, OccupationChoice, FencingChoice, MajorImprovementChoice, PlowingChoice, StableBuildingChoice, HouseBuildingChoice, ResourceTradingChoice)
from . import const, cards
from .utils import dotDict, recDotDefaultDict, dbgprint
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

class ResourcePayingStep(Step):
  def __init__(self, cost, trigger_name):
    self.trigger_name = trigger_name
    self.resources = [cost]

  def get_required_choice(self, game, player): 
    # TODO make choice
    return None

  def effect(self, game, player, choice):
    #TODO use choice
    selected_candidate = self.resources[0]
    player.change_state("", cost=selected_candidate)

class TakingResourcesFromActionStep(Step):
    def __init__(self, resources, executed_action):
        self.resources = resources.copy()
        self.executed_action = executed_action
        assert type(self.resources) == defaultdict

    def __str__(self):
        return '<%s>(%s)' % (self.__class__.__name__, str(self.resources)) 

    def get_required_choice(self, game, player):
        # TODO trigger event
        return ResourceTradingChoice(game, player, self.resources, self.executed_action)

    def effect(self, game, player, choice):
        selected_summary = choice.selected_summarized_candidate
        selected_candidate = choice.selected_candidate
        #if True or 'resources_to_board' in selected_candidate:
        if selected_candidate['resources_to_board']:
            self.executed_action.add_resources(selected_candidate['resources_to_board']) # take leftover back to the action if it exists.
            # raise NotImplementedError

        player.change_state("", change=selected_summary)
        # todo: ここでadditional_stepsからstepを取り出して返す

        #if selected_candidate['additional_steps']:
            #raise NotImplementedError
        return selected_candidate['additional_steps']

class RenovatingStep(Step):
  def __init__(self, resource):
    self.resource = resource

  def get_required_choice(self, game, player):
    return None

  def effect(self, game, player, choice):
    player.upgrade_house(self.resource)

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

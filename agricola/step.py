import abc
import itertools
from pprint import pprint
from future.utils import with_metaclass
from .choice import (ActionChoice, MinorImprovementChoice, SpaceChoice, OccupationChoice, FencingChoice, MajorImprovementChoice, PlowingChoice, StableBuildingChoice, HouseBuildingChoice, ResourceTradingChoice)
from . import const, cards
from .utils import dotDict, recDotDefaultDict, dbgprint
from collections import defaultdict

class Step(with_metaclass(abc.ABCMeta, object)):
    def __init__(self, player):
        self.player = player

    @abc.abstractmethod
    def get_required_choice(self, game):
        pass

    # returns next stack items
    def effect(self, game, choice):
        return None

class ActionSelectionStep(Step):
    def get_required_choice(self, game):
        return ActionChoice(game, self.player)

    def effect(self, game, choice):
        game.actions_taken[choice.choice_value] = self.player.index
        game.actions_remaining.remove(choice.choice_value)
        game.players[self.player.index].turn_left -= 1
        return choice.choice_value.effect(self.player)

class PlayOccupationStep(Step):
    def get_required_choice(self, game):
        # TODO set proper source
        return OccupationChoice(game, self.player)

    def effect(self, game, choice):
        self.player.play_occupation(choice.choice_value, game)
        return choice.choice_value.check_and_apply(self.player)

class PlayMajorImprovementStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return MajorImprovementChoice(game, self.player)

    def effect(self, game, choice):
        if not choice.choice_value:
            return
        if isinstance(choice.choice_value, cards.MinorImprovement):
            self.player.play_minor_improvement(choice.choice_value, game)
        if isinstance(choice.choice_value, cards.MajorImprovement):
            self.player.play_major_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(self.player)

class PlayMinorImprovementStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return MinorImprovementChoice(game, self.player)

    def effect(self, game, choice):
        self.player.play_minor_improvement(choice.choice_value, game)
        return choice.choice_value.check_and_apply(self.player)

class ResourcePayingStep(Step):
    def __init__(self, player, cost, trigger_name):
        super(ResourcePayingStep, self).__init__(player)
        self.trigger_name = trigger_name
        self.resources = [cost]

    def get_required_choice(self, game): 
        # TODO make choice
        return None

    def effect(self, game, choice):
        #TODO use choice
        selected_candidate = self.resources[0]
        self.player.change_state("", cost=selected_candidate)

class ResourceTradingStep(Step):
    def get_required_choice(self, game):
        #TODO magic string constant
        return ResourceTradingChoice(game, self.player, defaultdict(int), None, const.trigger_event_names.resource_trading)

    def effect(self, game, choice):
        selected_summary = choice.selected_summarized_candidate
        selected_candidate = choice.selected_candidate
        self.player.change_state("", change=selected_summary)

class TakingResourcesFromActionStep(Step):
    def __init__(self, player, resources, executed_action):
        super(TakingResourcesFromActionStep, self).__init__(player)
        self.resources = resources.copy()
        self.executed_action = executed_action
        assert type(self.resources) == defaultdict

    def __str__(self):
        return '<%s>(%s)' % (self.__class__.__name__, str(self.resources)) 

    def get_required_choice(self, game):
        # TODO trigger event
        return ResourceTradingChoice(game, self.player, self.resources, self.executed_action, const.trigger_event_names.take_resources_from_action)

    def effect(self, game, choice):
        selected_summary = choice.selected_summarized_candidate
        selected_candidate = choice.selected_candidate
        #if True or 'resources_to_board' in selected_candidate:
        if selected_candidate['resources_to_board']:
            self.executed_action.add_resources(selected_candidate['resources_to_board']) # take leftover back to the action if it exists.
            # raise NotImplementedError

        self.player.change_state("", change=selected_summary)

        if 'additional_steps' not in selected_candidate:
          return []
        return selected_candidate['additional_steps']

class RenovatingStep(Step):
  def __init__(self, player, resource):
    super(RenovatingStep, self).__init__(player)
    self.resource = resource

  def get_required_choice(self, game):
    return None

  def effect(self, game, choice):
    self.player.upgrade_house(self.resource)

class PlowingStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return PlowingChoice(game, self.player)

    def effect(self, game, choice):
        self.player.plow_fields(choice.choice_value)

class HouseBuildingStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return HouseBuildingChoice(game, self.player)
    
    def effect(self, game, choice):
        if choice.choice_value:
          self.player.build_rooms(choice.choice_value)
          return [HouseBuildingStep(self.player)]

class StableBuildingStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return StableBuildingChoice(game, self.player)

    def effect(self, game, choice):
        if choice.choice_value:
            self.player.build_stables(choice.choice_value, 2)
            return [StableBuildingStep(self.player)]

class SowingStep(Step):
    pass

class BakingStep(Step):
    pass

class FencingStep(Step):
    def get_required_choice(self, game):
        # TODO set source
        return FencingChoice(game, self.player)
    
    def effect(self, game, choice):
        if choice.choice_value:
            self.player.build_pastures(choice.choice_value)

class AnimalMarketStep(Step):
    pass

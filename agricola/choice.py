import abc
from collections import defaultdict
from .player import Pasture
from .utils import dbgprint
from . import const

class Choice(object):
    def __init__(self, game, player, desc=None):
        self.game = game
        self.player = player
        self.desc = desc

        self.selected_candidate_idx = 0
        self.candidates = self._get_candidates()
        self.summarized_candidates = self._summarize_candidates(self.candidates)

        self.validate()

    @property
    def name(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def validate(self):
        pass

    # returns next required choice class
    @property
    def next_choices(self):
        return []

    def _get_candidates(self):
        return [] # todo: list up default candidates + trigger occupations and improvements?
    def _summarize_candidates(self, candidates):
        return candidates

    @property
    def selected_summarized_candidate(self):
        return self.summarized_candidates[self.selected_candidate_idx]

    @property
    def selected_candidate(self):
        return self.candidates[self.selected_candidate_idx]
    
    @abc.abstractmethod
    def read_players_choice(self, choice_dict):
        pass

class ActionChoice(Choice):
    '''
    ActionChoice sample
    {
        "action_id": "Fencing"
    }
    '''
    def read_players_choice(self, choice_dict):
        if "action_id" in choice_dict:
            target_action = [action for action in self.game.actions_remaining if action.name == choice_dict["action_id"]]
            # TODO think about error
            self.choice_value = target_action[0]
        else:
            self.choice_value = None

class OccupationChoice(Choice):
    def read_players_choice(self, choice_dict):
        if "occupation_id" in choice_dict:
            target_occupation = [occupation for occupation in self.player.hand["occupations"] if occupation.name == choice_dict["occupation_id"]]
            # TODO think about error
            self.choice_value = target_occupation[0]
        else:
            self.choice_value = None

class MinorImprovementChoice(Choice):
    def read_players_choice(self, choice_dict):
        if "minor_improvement_id" in choice_dict:
            target_improvement = [minor_improvement for minor_improvement in self.player.hand["minor_improvements"] if minor_improvement.name == choice_dict["minor_improvement_id"]]
            # TODO think about error
            self.choice_value = target_improvement[0]
        else:
            self.choice_value = None

class MajorImprovementChoice(Choice):
    def read_players_choice(self, choice_dict):
        if "improvement_id" in choice_dict:
            target_improvement = [minor_improvement for minor_improvement in self.player.hand["minor_improvements"] if minor_improvement.name == choice_dict["improvement_id"]]
            if len(target_improvement) != 0:
                # TODO think about error
                self.choice_value = target_improvement[0]
                return
            target_improvement = [major_improvement for major_improvement in self.game.major_improvements if major_improvement.name == choice_dict["improvement_id"]]
            if len(target_improvement) != 0:
                # TODO think about error
                self.choice_value = target_improvement[0]
                return
        else:
            self.choice_value = None

class FencingChoice(Choice):
    '''
     FencingChoice Sample
    {
        "pastures": [
            [
                [4,1],
                [4,2],
                [3,1],
                [3,2]
            ]
        ]
    }
    '''
    def read_players_choice(self, choice_dict):
        if "pastures" in choice_dict:
            self.choice_value = list(map(lambda p_array: Pasture(list(map(lambda pasture: (pasture[1], pasture[0]), p_array))), choice_dict["pastures"]))
        else:
            self.choice_value = None

class SpaceChoice(Choice):
    '''
    SpaceChoice input Sample
    {
        "space": [4,0]
    }
    '''
    def read_players_choice(self, choice_dict):
        if "space" in choice_dict:
            self.choice_value = [(choice_dict["space"][1], 
                                  choice_dict["space"][0])]
        else:
            self.choice_value = None

class HouseBuildingChoice(SpaceChoice):
    pass

class StableBuildingChoice(SpaceChoice):
    pass

class PlowingChoice(SpaceChoice):
    pass

class ResourceTradingChoice(Choice):
    def __init__(self, game, player, resources, executed_action, trigger_event_name, desc=None):
        self.resources = resources
        self.executed_action = executed_action
        self.trigger_event_name = trigger_event_name
        super(ResourceTradingChoice, self).__init__(game, player, desc=desc)

    def _get_candidates(self):
        choice_candidates = [({
            'action_resources': self.resources, 
            'additional_resources': defaultdict(int),
            'additional_steps': [],
            'resources_to_board':defaultdict(int)
        })]
        # TODO check occupation and improvements
        choice_filters = self.player.trigger_event(self.trigger_event_name, self.player,  resource_choices=choice_candidates)

        # TODO think about junretu
        for choice_filter in choice_filters:
            choice_candidates = choice_filter(self.player, choice_candidates, self.executed_action)
        self.choice_candidates = choice_candidates
        return choice_candidates

    def _summarize_candidates(self, candidates):
        summarized = []
        for c in candidates:
            sc = defaultdict(int)
            for k, v in c['action_resources'].items():
                sc[k] += v
            for k, v in c['additional_resources'].items():
                sc[k] += v
            summarized.append(sc)
        return summarized

    def read_players_choice(self, choice_dict):
        # todo; ここでagentからの入力をもとにselected_candidate_idxを更新
        #self.selected_candidate_idx = random.choice(range(len(self.candidates)))
        self.selected_candidate_idx = len(self.candidates) - 1
        


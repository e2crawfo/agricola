import abc
from .player import Pasture

class Choice(object):
    def __init__(self, game, player, choice_dict, desc=None):
        self.desc = desc
        self.player = player
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

    @classmethod
    def get_candidates(self_cls, game, player):
        return [] # todo: list up default candidates + trigger occupations and improvements?

class ActionChoice(Choice):
    '''
    ActionChoice sample
    {
        "action_id": "Fencing"
    }
    '''
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(ActionChoice, self).__init__(game, player, choice_dict)
        if "action_id" in choice_dict:
            target_action = [action for action in game.actions_remaining if action.name == choice_dict["action_id"]]
            # TODO think about error
            self.choice_value = target_action[0]
        else:
            self.choice_value = None

class OccupationChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(OccupationChoice, self).__init__(game, player, choice_dict)
        if "occupation_id" in choice_dict:
            target_occupation = [occupation for occupation in player.hand["occupations"] if occupation.name == choice_dict["occupation_id"]]
            # TODO think about error
            self.choice_value = target_occupation[0]
        else:
            self.choice_value = None

class MinorImprovementChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(MinorImprovementChoice, self).__init__(desc, game, player, choice_dict)
        if "minor_improvement_id" in choice_dict:
            target_improvement = [minor_improvement for minor_improvement in player.hand["minor_improvements"] if minor_improvement.name == choice_dict["minor_improvement_id"]]
            # TODO think about error
            self.choice_value = target_improvement[0]
        else:
            self.choice_value = None

class MajorImprovementChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(MajorImprovementChoice, self).__init__(desc, game, player, choice_dict)
        if "improvement_id" in choice_dict:
            target_improvement = [minor_improvement for minor_improvement in player.hand["minor_improvements"] if minor_improvement.name == choice_dict["improvement_id"]]
            if len(target_improvement) != 0:
                # TODO think about error
                self.choice_value = target_improvement[0]
                return
            target_improvement = [major_improvement for major_improvement in game.major_improvements if major_improvement.name == choice_dict["improvement_id"]]
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
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(FencingChoice, self).__init__(game, player, choice_dict)
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
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(SpaceChoice, self).__init__(game, player, choice_dict)
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
  @classmethod
  def get_candidates(self_cls, game, player):
    self.resources = resources.copy()
    self.resource_choices = [({'action_resources': self.resources, 'additional_resources': defaultdict(int)})]
    # TODO check occupation and improvements
    resource_choice_filters = player.trigger_event(const.trigger_event_names.take_resources_from_action, player, resource_choices=self.resource_choices)

    # TODO think about junretu
    for resource_choice_filter in resource_choice_filters:
      self.resource_choices = resource_choice_filter(self.resource_choices)





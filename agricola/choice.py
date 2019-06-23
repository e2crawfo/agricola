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

# ActionChoise sample
# {
#   "action_id": "Fencing"
# }
class ActionChoice(Choice):
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

class AnimalMarketchoice(Choice):
    def validate(self):
        pass

class Expansionchoice(Choice):
    def validate(self):
        pass

class Stablechoice(Choice):
    def validate(self):
        pass

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

class FarmlandChoice(Choice):
    def validate(self):
        pass

class BakingChoice(Choice):
    def validate(self):
        pass

class SowingChoice(Choice):
    def validate(self):
        pass

# FencingChoice Sample
# {
#   "pastures": [
#     [
#       [4,1],
#       [4,2],
#       [3,1],
#       [3,2]
#     ]
#   ]
# }
class FencingChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(FencingChoice, self).__init__(game, player, choice_dict)
        if "pastures" in choice_dict:
            self.choice_value = list(map(lambda p_array: Pasture(list(map(lambda pasture: (pasture[1], pasture[0]) ,p_array))), choice_dict["pastures"]))
        else:
            self.choice_value = None

# old choices

class DictChoice(Choice):
    def __init__(self, choice_dict, desc=None):
        self.choice_dict = choice_dict
        super(DictChoice, self).__init__(desc)

class YesNoChoice(Choice):
    def __init__(self, desc=None):
        super(DiscreteChoice, self).__init__(desc)


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
    def __init__(self, subchoice, desc=None, mx=None):
        super(VariableLengthListChoice, self).__init__(desc)
        self.subchoice = subchoice
        self.mx = mx

# SpaceChoice Sample
# {
#     "space": [4,0]
# }
class SpaceChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(SpaceChoice, self).__init__(game, player, choice_dict)
        if "space" in choice_dict:
            self.choice_value = [(choice_dict["space"][1], choice_dict["space"][0])]
        else:
            self.choice_value = None
import abc

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
        super(OccupationChoice, self).__init__(desc, choice_dict)
        if "occupation_id" in choice_dict:
            target_occupation = [occupation for occupation in player.hand["occupations"] if occupation.name == choice_dict["occupation_id"]]
            # TODO think about error
            self.choice_value = target_occupation[0]
        else:
            self.choice_value = None

    @property
    def next_choices(self):
        if self.choice_value:
            return self.choice_value.next_choices
        return None

    def validate(self):
        pass

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

    @property
    def next_choices(self):
        if self.choice_value:
            return self.choice_value.next_choices
        return None

    def validate(self):
        pass

class MajorImprovementChoice(Choice):
    def validate(self):
        pass

class FarmlandChoice(Choice):
    def validate(self):
        pass

class BakingChoice(Choice):
    def validate(self):
        pass

class SowingChoice(Choice):
    def validate(self):
        pass

class FencingChoice(Choice):
    def validate(self):
        pass

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


class SpaceChoice(Choice):
    def __init__(self, game, player, choice_dict, desc=None, mx=None):
        super(SpaceChoice, self).__init__(game, player, choice_dict)
        self.choice_value = [(choice_dict["space"][1], choice_dict["space"][0])]

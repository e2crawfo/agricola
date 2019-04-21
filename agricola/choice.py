class Choice(object):
    def __init__(self, desc=None):
        self.desc = desc

    def validate(self, choice):
        pass

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
    def __init__(self, desc=None):
        super(SpaceChoice, self).__init__(desc)

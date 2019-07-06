import abc
from future.utils import with_metaclass

from agricola.utils import score_mapping, cumsum
from agricola.choice import (
    SpaceChoice)
from agricola.step import PlowingStep
from agricola import const
import copy
from agricola.errors import (
  AgricolaException, AgricolaNotEnoughResources, AgricolaLogicError,
  AgricolaPoorlyFormed, AgricolaImpossible)


def all_subclasses(cls):
    recurse = [
        g for s in cls.__subclasses__() for g in all_subclasses(s)]
    return cls.__subclasses__() + recurse

class Card(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractproperty
    def card_type(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def short_name(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{0}({1})>".format(self.name, self.card_type)

class AgricolaException(Exception):
    """ General Agricola exception. """
    pass


class AgricolaNotEnoughResources(AgricolaException):
    """ Raised when a player does not have sufficent
        resources to pay for a requested action.
    """
    pass


class AgricolaLogicError(AgricolaException):
    """ Raised when action is requested that violates
        the rules of Agricola.
    """
    pass


class AgricolaPoorlyFormed(AgricolaLogicError):
    """ Raised when an updated is requested that
        is not well-formed.
    """
    pass


class AgricolaInvalidChoice(AgricolaLogicError):
    """ Raised when an updated is requested that
        is not well-formed.
    """
    pass


class AgricolaImpossible(AgricolaLogicError):
    """ Raised when an update is requested that cannot
        be performed given the current state.
    """
    pass


from .player import Player
from .ui import TextInterface

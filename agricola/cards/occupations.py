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

from agricola.cards.base import all_subclasses, Card

def get_occupations(n_players):
    # DEBUG
    occupations = []
    for i in range(0, 100):
       occupations.append(Woodcutter())
    return occupations
    ####################

    occ_classes = all_subclasses(Occupation)
    return [o() for o in occ_classes if o.min_players <= n_players]

class Occupation(with_metaclass(abc.ABCMeta, Card)):
     # returns steps
    def check_and_apply(self, player):
        print("Applying occupation {0}.".format(self.name))

        self._check(player)
        return self._apply(player)

    def _check(self, player):
        pass

    def _apply(self, player):
        pass

    @property
    def card_type(self):
        return "Occupation"

    @abc.abstractproperty
    def deck(self):
        pass

    @abc.abstractproperty
    def min_players(self):
        pass

    @abc.abstractproperty
    def text(self):
        pass

    @property
    def next_choices(self):
        return []

    def victory_points(self, player):
        return 0

# TODO implement
class Lover(Occupation):
    deck = 'K'
    id = 291
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class ReedCollector(Occupation):
    deck = 'E'
    id = 205
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(1, 5), 'reed', 1)

# TODO implement
class PigWhisperer(Occupation):
    deck = 'K'
    id = 302
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class BerryPicker(Occupation):
    deck = 'E'
    id = 152
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class CattleWhisperer(Occupation):
    deck = 'E'
    id = 201
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Cowhead(Occupation):
    deck = 'I'
    id = 240
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Dancer(Occupation):
    deck = 'E'
    id = 212
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class StreetMusician(Occupation):
    deck = 'I'
    id = 257
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Tutor(Occupation):
    deck = 'E'
    id = 174
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class Woodcutter(Occupation):
    deck = 'E'
    id = 176
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.listen_for_event(self, const.trigger_event_names.take_resources_from_action)

    def trigger(self, player, **kwargs):
        return self.resource_choice_filter

    def resource_choice_filter(self, resource_choices):
        result = []
        for resource_choice in resource_choices:
            choice = copy.deepcopy(resource_choice)
            if "wood" in choice["action_resources"] and choice["action_resources"]["wood"] >= 1:
                choice["additional_resources"]["wood"] += 1
            result.append(choice)
        return result

# TODO implement
class Conjurer(Occupation):
    deck = 'E'
    id = 167
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SeasonalWorker(Occupation):
    deck = 'E'
    id = 202
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class ChurchWarden(Occupation):
    deck = 'I'
    id = 227
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class LordOfTheManor(Occupation):
    deck = 'E'
    id = 189
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Cook(Occupation):
    deck = 'E'
    id = 181
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Midwife(Occupation):
    deck = 'I'
    id = 232
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class YeomanFarmer(Occupation):
    deck = 'E'
    id = 165
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Outrider(Occupation):
    deck = 'I'
    id = 261
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class CharcoalBurner(Occupation):
    deck = 'E'
    id = 182
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Chief(Occupation):
    deck = 'E'
    id = 172
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SeedSeller(Occupation):
    deck = 'K'
    id = 296
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Undergardener(Occupation):
    deck = 'E'
    id = 166
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Farmer(Occupation):
    deck = 'E'
    id = 160
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class FieldWatchman(Occupation):
    deck = 'I'
    id = 225
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Patron(Occupation):
    deck = 'E'
    id = 192
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class MasterShepherd(Occupation):
    deck = 'E'
    id = 204
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class SheepWhisperer(Occupation):
    deck = 'I'
    id = 250
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Swineherd(Occupation):
    deck = 'E'
    id = 206
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class Braggart(Occupation):
    deck = 'E'
    id = 197
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class WoodCollector(Occupation):
    deck = 'I'
    id = 235
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(1, 6), 'wood', 1)

class WoodDeliveryman(Occupation):
    deck = 'K'
    id = 283
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(8, 15), 'wood', 1, absolute=True)

# TODO implement
class Greengrocer(Occupation):
    deck = 'E'
    id = 168
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

# TODO implement
class ClayWorker(Occupation):
    deck = 'K'
    id = 290
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

class ClayDeliveryman(Occupation):
    deck = 'E'
    id = 187
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        player.add_future(range(8, 15), 'clay', 1, absolute=True)

# TODO implement
class ClayMixer(Occupation):
    deck = 'E'
    id = 188
    min_players = 1
    text = ''

    def check_and_apply(self, player):
        pass

    def trigger(self, player, **kwargs):
        pass

import abc
import itertools
from collections import OrderedDict, Counter, defaultdict
from future.utils import with_metaclass
from copy import deepcopy
from pprint import pformat

import numpy as np
import networkx as nx

from .utils import (
  EventGenerator, EventScope, multiset_satisfy, draw_grid,
  index_check, orthog_adjacent, score_mapping)
from .errors import (
  AgricolaException, AgricolaNotEnoughResources, AgricolaLogicError,
  AgricolaPoorlyFormed, AgricolaImpossible)


class SpatialObject(with_metaclass(abc.ABCMeta, object)):
  def __str__(self):
    space_strs = ["({0}, {1})".format(s[0], s[1])
            for s in sorted(self.spaces)]
    space_str = ", ".join(space_strs)
    return "<" + self.__class__.__name__ + " " + space_str + ">"

  def __repr__(self):
    return str(self)

  def index_check(self, shape):
    """ Check that all of my spaces lie within the confines of a board with given shape. """
    for s in self.spaces:
      index_check(s, shape)

  def overlaps(self, other):
    return bool(self.spaces & other.spaces)

  def __contains__(self, space):
    return space in self.spaces

  @property
  def spaces(self):
    return set(self._spaces)

  @staticmethod
  def orthog_graph(objects, require_connected=True):
    """ Create an undirected graph from a collection of spatial objects.

    Two objects are connected in the graph iff those objects are
    orthogonally adjacent to one another.

    """
    if isinstance(objects, SpatialObject):
      objects = [objects]

    G = nx.Graph()
    for o in objects:
      G.add_nodes_from(o.spaces)

    for s0, s1 in itertools.combinations(G.nodes(), 2):
      if orthog_adjacent(s0, s1):
        G.add_edge(s0, s1)

    if require_connected:
      if len(G) > 1 and not nx.is_connected(G):
        s = '{' + ', '.join([str(o) for o in objects]) + '}'
        raise AgricolaLogicError(
          "Group of SpatialObjects {0} does not form a "
          "connected region.".format(s))
    return G

  @staticmethod
  def check_connected_group(objects):
    """ Check that a group of SpatialObjects are connected. """
    SpatialObject.orthog_graph(objects, require_connected=True)


class SingleSpaceObject(SpatialObject):
  def __init__(self, space):
    self.space = space

  @property
  def spaces(self):
    return [self.space]


class Field(SingleSpaceObject):
  def __init__(self, space, n_items=0, kind=None):
    self.space = space
    if bool(n_items) != bool(kind):
      raise ValueError(
        "Either neither or both of ``n_items`` and "
        "``kind`` must be supplied. Got {0} and {1}.".format(n_items, kind))
    self._n_items = n_items
    self._kind = kind

  def is_empty(self):
    return self.n_items == 0

  def plant_grain(self):
    if not self.is_empty():
      raise AgricolaLogicError("Attempting to plant grain in a non-empty field.")
    self._n_items = 3
    self._kind = 'grain'

  def plant_veg(self):
    if not self.is_empty():
      raise AgricolaLogicError("Attempting to plant veg in a non-empty field.")
    self._n_items = 2
    self._kind = 'veg'

  @property
  def n_items(self):
    return self._n_items

  @property
  def kind(self):
    return self._kind

  def harvest(self):
    if self._n_items > 0:
      self._n_items -= 1
      if self._n_items == 0:
        self._kind = None
      return True
    return False


class Room(SingleSpaceObject):
  pass


class AnimalContainer(object):
  @abc.abstractmethod
  def capacity(self):
    return 0


class Stable(SingleSpaceObject, AnimalContainer):
  def capacity(self):
    return 1


class Pasture(SpatialObject, AnimalContainer):
  def __init__(self, spaces):
    if isinstance(spaces[0], int):
      spaces = [spaces]
    self._spaces = spaces = list(set(spaces))

    # Check that the spaces in the pasture are connected.
    SpatialObject.check_connected_group(
      [SingleSpaceObject(s) for s in self.spaces])

    self.size = len(self.spaces)

    self.n_stables = 0

    fences = []
    for s in self.spaces:
      fences.append(((s[0], s[1]), (s[0], s[1]+1)))  # Top
      fences.append(((s[0], s[1]+1), (s[0]+1, s[1]+1)))  # Right
      fences.append(((s[0]+1, s[1]), (s[0]+1, s[1]+1)))  # Bottom
      fences.append(((s[0], s[1]), (s[0]+1, s[1])))  # Left

    counts = Counter(fences)
    self._fences = [f for f, c in counts.items() if c == 1]

  @property
  def fences(self):
    return self._fences

  @staticmethod
  def fences_for_pasture_group(pastures):
    fences = set()
    for p in pastures:
      for f in p.fences:
        fences.add(f)
    return set(fences)

  def adjacent_to(self, other):
    for s in self.spaces:
      for so in other.spaces:
        if orthog_adjacent(s, so):
          return True
    return False

  def add_stables(self, n=1):
    self.n_stables += n

  def capacity(self):
    return self.n_spaces * 2**(self.n_stables+1)
  
RESOURCE_TYPES = ('food wood clay stone reed sheep boar cattle grain veg '
          'pastures fences fences_avail stables fenced_stables free_stables stables_avail '
          'rooms people people_avail grain_fields veg_fields empty_fields fields '
          'empty_spaces used_spaces')
RESOURCE_TYPES = RESOURCE_TYPES.split(' ')
ANIMALS = ['sheep', 'boar', 'cattle']


class PlayerStateChange(object):
  """ Encapsulates a change to a Player object.

  Supposed to allow atomic changes, so that a set of changes will be completely
  applied if an only if a set of conditions are all met.

  Parameters
  ----------
  description: str
    Textual description of the change to effect.
  change: dict (str -> int) (optional)
    Dictionary mapping from resource names to integers
    specifying the delta to be applied for that resource. This
    argument can be omitted, in which case this object simply
    checks that the supplied prereq are satisfied. No resource amounts
    are permitted to go below 0.
  prereq: dict (str -> int) (optional)
    Dictionary mapping from resource names to positive integers
    specifying the minimum amount of that resource required
    for applying this state change. This argument can be omitted.
    Some things that seem like prereqs can actually be supplied
    as changes.
  cost: dict (str -> int) (optional)
    Similar to prereq, except that the amount required is also subtracted
    from the players reserves. So more like a combination of a `change` and a `prereq`.
  change_fns: list of fn (player, game)
    List of functions, each accepting a player and a game, and returning None.
    Allowed to make modifications to the player, should not alter the game.
  prereq_fns: list of fn (player, game)
    List of functions, each accepting a player and a game, and returning a boolean
    giving whether the player meets the prerequisites checked by that function.
    Should not alter the player or the game.

  """
  def __init__(
      self, description, change=None, prereq=None, cost=None,
      change_fns=None, prereq_fns=None):
    self.description = description

    self.change = change or {}
    self.prereq = prereq or {}
    self.cost = cost or {}

    self.change_fns = change_fns or []
    self.prereq_fns = prereq_fns or []

    for k, v in self.change.items():
      if k not in RESOURCE_TYPES:
        raise AgricolaLogicError(
          "Malformed PlayerStateChange object. "
          "{0} is not a valid resource type.".format(k))

  def check_and_apply(self, player):
    for k, v in self.prereq.items():
      if getattr(player, k) < v:
        raise AgricolaNotEnoughResources(self._error_message(player))

    for k, v in self.cost.items():
      if getattr(player, k) < v:
        # begging card
        if k == "food":
          player.begging_cards += v - getattr(player, k)
          player.add_resources(food= v - getattr(player, k))
        else:
          raise AgricolaNotEnoughResources(self._error_message(player))

    for fn in self.prereq_fns:
      if not fn(self, self.game):
        raise AgricolaException("Prerequisite unsatisfied.")

    for k, v in self.change.items():
      setattr(player, k, getattr(player, k) + v)

    for k, v in self.cost.items():
      setattr(player, k, getattr(player, k) - v)

    for fn in self.change_fns:
      fn(self, self.game)

  def _error_message(self, player):
    s = [self.description + ' requires']

    prereq = self.prereq.copy()
    prereq.update(self.cost)

    pairs = list(prereq.items())

    _s = []
    for k, v in pairs:
      _s.append("{0} {1}".format(v, k))
    s.append('/'.join(_s))

    s.append("but player only has")

    _s = []
    for k, v in pairs:
      _s.append("{0} {1}".format(getattr(player, k), k))
    s.append('/'.join(_s))

    return ' '.join(s)


class Player(EventGenerator):
  # TODO: In the constructor, just set all self attributes without doing checks. Then at the end, call a function
  # which checks that constraints are satisfied.

  # TODO: implement harvest. A bit tough because player harvests veg, then has to make a decision about whether to cook it or not (or eat the grain raw).

  # TODO: handle babies vs people.

  # TODO: handle case where people build pastures on top of already existing pastures, e.g. by adding fences inside an existing pasture.

  # TODO: Restrict when and how many times cooking can be
  # done (e.g. joinery (wood to food) can only be done once per harvest).

  # TODO: beggar tokens
  def __init__(
      self, name, shape=None, house_type='wood',
      rooms=None, fields=None, stables=None, pastures=None,
      food=0, wood=0, clay=0, stone=0, reed=0,
      sheep=0, boar=0, cattle=0, grain=0, veg=0,
      people=2, people_avail=3, fences_avail=15, stables_avail=4,
      occupations=None, minor_improvements=None, major_improvements=None, hand=None):
    super(Player, self).__init__()
    self.name = name
    self.begging_cards = 0

    self.people = people
    self.people_avail = people_avail

    self.resources = dict(
      food=food, wood=wood, clay=clay, stone=stone, reed=reed,
      grain=grain, veg=veg)
    self.animals = dict(sheep=sheep, boar=boar, cattle=cattle)

    if shape is None:
      shape = (3, 5)
    self.shape = shape

    self.house_type = house_type

    if rooms is None:
      rooms = [(0, 0), (1, 0)]
    self._rooms = rooms = [Room(r) for r in rooms]

    pastures = pastures or []
    self._pastures = pastures = [Pasture(p) for p in pastures]
    self.fences_avail = fences_avail

    stables = stables or []
    self._stables = stables = [Stable(s) for s in stables]
    self.stables_avail = stables_avail

    fields = fields or []
    self._fields = fields = [Field(f) for f in fields]

    # Played cards
    self.occupations = occupations or []
    self.minor_improvements = minor_improvements or []
    self.major_improvements = major_improvements or []
    self.played_cards = {
      attr: getattr(self, attr)
      for attr in ['occupations', 'minor_improvements', 'major_improvements']}

    # Hand cards
    hand = hand or {'minor_improvements': [], 'occupations': []}
    self.hand = deepcopy(hand)

    self.house_progression = dict(wood=['clay'], clay=['stone'], stone=[])
    self.room_cost = 5

    # The last rate in this list can be applied infinitely
    # many times during a turn.
    self.bread_rates = [0]

    self.cooking_rates = dict(grain=1, veg=1, sheep=0, boar=0, cattle=0)
    self.harvest_rates = dict(wood=[], clay=[], reed=[])

    self.occupied = OrderedDict()

    self._check_spatial_objects(self._rooms, 'room')
    Room.check_connected_group(self._rooms)
    self.occupied['room'] = self._rooms

    self._check_spatial_objects(self._pastures, 'pasture', omit='stable')
    Pasture.check_connected_group(self._pastures)
    self.occupied['pasture'] = self._pastures

    self._check_spatial_objects(self._stables, 'stable', omit='pasture')
    self.occupied['stable'] = self._stables

    self._check_spatial_objects(self._fields, 'field')
    Field.check_connected_group(self._fields)
    self.occupied['field'] = self._fields

    # round_idx -> dictionary of resources
    self.futures = defaultdict(lambda: defaultdict(int))

    self.pasture_capacity_modifier = 0

    self.game = None

  def _validate_event_name(self, event_name):
    return event_name in [
      'start_round',
      'start_stage',
      'end_round',
      'end_stage',
      'field_phase',
      'feeding_phase',
      'breeding_phase',
      'renovation',
      'build_room',
      'build_pasture',
      'build_stable'
      'plow_field',
      'birth',
      'occupation',
      'minor_improvement',
      'major_improvement'
    ] or event_name.startswith('Action: ')

  def set_game(self, game):
    self.game = game

  def __getattr__(self, key):
    if key in ["resources", "animals"]:
      return self.__getattribute__(key)

    if hasattr(self, "resources") and key in self.resources:
      return self.resources[key]
    if hasattr(self, "animals") and key in self.animals:
      return self.animals[key]

    return self.__getattribute__(key)

  def give_cards(self, attr, cards):
    self.hand[attr].extend(cards)

  @property
  def rooms(self):
    return len(self._rooms)

  @property
  def pastures(self):
    return len(self._pastures)

  @property
  def fences(self):
    return Pasture.fences_for_pasture_group(self._pastures)

  @property
  def stables(self):
    return len(self._stables)

  @property
  def fenced_stables(self):
    return len([s for s in self._stables
          if any(s in p for p in self.pastures)])

  @property
  def free_stables(self):
    return len([s for s in self._stables
          if not any(s in p for p in self.pastures)])

  @property
  def fields(self):
    return len(self._fields)

  @property
  def grain_fields(self):
    return len([f for f in self._fields if f.kind == 'grain'])

  @property
  def veg_fields(self):
    return len([f for f in self._fields if f.kind == 'veg'])

  @property
  def empty_fields(self):
    return len([f for f in self._fields if f.kind is None])

  @property
  def room_spaces(self):
    return [s for room in self._rooms for s in room.spaces]

  @property
  def pasture_spaces(self):
    return [s for pasture in self._pastures for s in pasture.spaces]

  @property
  def stable_spaces(self):
    return [s for stable in self._stables for s in stable.spaces]

  @property
  def field_spaces(self):
    return [s for field in self._fields for s in field.spaces]

  @property
  def used_spaces(self):
    return (set(self.room_spaces) | set(self.pasture_spaces) |
        set(self.stable_spaces) | set(self.field_spaces))

  @property
  def empty_spaces(self):
    used_spaces = self.used_spaces
    empty_spaces = set()
    for i in range(self.shape[0]):
      for j in range(self.shape[1]):
        if (i, j) not in used_spaces:
          empty_spaces.add((i, j))
    return empty_spaces

  def __str__(self):
    s = ["<Player {} \n".format(self.name)]
    grid = np.tile('.', self.shape)

    room_spaces = set(self.room_spaces)
    stable_spaces = set(self.stable_spaces)
    field_spaces = set(self.field_spaces)

    for i in range(self.shape[0]):
      for j in range(self.shape[1]):
        space = i, j
        if space in room_spaces:
          grid[space] = 'H'
        elif space in stable_spaces:
          grid[space] = '^'
        elif space in field_spaces:
          grid[space] = '~'
    s.append(draw_grid(grid, (3, 5), self.fences))
    x = []
    for key in 'food wood clay stone reed sheep boar cattle grain veg'.split(' '):
      x.append("{0}: {1}".format(key, getattr(self, key)))
    s.append(', '.join(x))

    s.append("Played cards:")
    s.append(pformat(self.played_cards, indent=1))

    s.append("Hand:")
    s.append(pformat(self.hand, indent=1))

    s.append("SCORE: {0}".format(self.score()))
    s.append(">")
    return '\n'.join(s)

  def score(self):
    score = 0

    score += score_mapping(self.pastures, [1, 2, 3, 4], [-1, 1, 2, 3, 4])
    score += score_mapping(self.fields, [1, 3, 4, 5], [-1, 1, 2, 3, 4])

    score += score_mapping(self.grain, [1, 4, 6, 8], [-1, 1, 2, 3, 4])
    score += score_mapping(self.veg, [1, 2, 3, 4], [-1, 1, 2, 3, 4])

    score += score_mapping(self.sheep, [1, 4, 6, 8], [-1, 1, 2, 3, 4])
    score += score_mapping(self.boar, [1, 3, 5, 7], [-1, 1, 2, 3, 4])
    score += score_mapping(self.cattle, [1, 2, 4, 6], [-1, 1, 2, 3, 4])

    score += max(self.fenced_stables, 4)
    score -= len(self.empty_spaces)

    score += 3 * self.people

    multiplier = {'wood': 0, 'clay': 1, 'stone': 2}[self.house_type]
    score += multiplier * self.rooms

    score += sum([occ.victory_points(self) for occ in self.occupations])
    score += sum([imp.victory_points(self) for imp in self.minor_improvements])
    score += sum([imp.victory_points(self) for imp in self.major_improvements])

    score -= 3 * self.begging_cards

    return score

  def start_round(self, round_idx):
    with EventScope(self, 'start_round'):
      resources = self.futures[round_idx]

      for resource, amount in resources.items():
        # TODO: handle fields differently than the other resources
        pass

  def end_round(self):
    with EventScope(self, 'end_round'):
      pass

  def harvest(self):
    # harvest from field
    for field in self._fields:
      kind = field.kind
      if field.harvest():
        self.add_resources(**{kind: 1})

    # pay foods
    state_change = PlayerStateChange("harvest", cost={"food": 2 * self.people})
    state_change.check_and_apply(self)


  def _check_spatial_objects(self, objects, name, omit=None):
    omit = omit or []
    if isinstance(objects, SpatialObject):
      objects = [objects]

    try:
      for o in objects:
        o.index_check(self.shape)
    except IndexError as e:
      raise AgricolaLogicError(str(e))

    spaces = []
    for o in objects:
      spaces.extend(o.spaces)
    counts = Counter(spaces)
    for k, v in counts.items():
      if v > 1:
        raise AgricolaImpossible(
          "Trying to add two {0}s that "
          "overlap at space {1}.".format(name, k))

    for object_type, objects in self.occupied.items():
      if object_type not in omit:
        for space in spaces:
          if any(space in o for o in objects):
            raise AgricolaImpossible(
              "Trying to place a {0} at space {1} where "
              "a {2} already exists.".format(
                name, space, object_type))

  def add_future(self, rounds, resource, amount, absolute=False):
    offset = 0 if absolute else self.game.round_idx
    for r in rounds:
      self.futures[offset + r][resource] += amount

  def add_people(self, n=1):
    if self.people_avail < n:
      raise AgricolaImpossible(
        "Trying to add {0} people, but player has only {1} people "
        "available.".format(n, self.people_avail))
    self.people += n
    self.people_avail -= n

  def add_resources(self, **resources):
    for r in resources:
      if r not in self.resources:
        raise AgricolaPoorlyFormed("{0} is not a resource type".format(r))

    description = "Adding resources "
    state_change = PlayerStateChange(description, change=resources)
    state_change.check_and_apply(self)

  def add_animals(self, **animals):
    for animal, count in animals.items():
      if animal not in self.animals:
        raise AgricolaPoorlyFormed("{0} is not an animal type".format(animal))

      animal_counts = self.animals.copy()
      animal_counts[animal] += count
      self._check_animal_capacity(animal_counts.values(), count, animal)
      self.animals[animal] += count

  def change_state(self, description, change=None, prereq=None, cost=None):
    state_change = PlayerStateChange(description, change=change, prereq=prereq, cost=cost)
    state_change.check_and_apply(self)

  def build_rooms(self, spaces):
    rooms = [Room(s) for s in spaces]

    self._check_spatial_objects(rooms, 'room')
    Room.check_connected_group(self._rooms + rooms)

    n_rooms = len(spaces)

    description = "Building {0} rooms".format(n_rooms)
    cost = {self.house_type: self.room_cost * n_rooms, 'reed': 2 * n_rooms}
    state_change = PlayerStateChange(description, cost=cost)
    state_change.check_and_apply(self)

    self._rooms.extend(rooms)

  def valid_house_upgrades(self):
    return self.house_progression[self.house_type]

  def upgrade_house(self, material):
    assert material in self.valid_house_upgrades(), (
      "Cannot upgrade from {} to {}.".format(self.house_type, material))
    description = "Upgrading house from {0} to {1}".format(self.house_type, material)
    cost = {self.material_required: self.n_rooms, 'reed': 1}
    state_change = PlayerStateChange(description, cost=cost)
    state_change.check_and_apply(self)
    self.house_type = material

  def build_pastures(self, pastures):
    """ Construct supplied Pastures.

    If the player possesses insufficient wood for building them,
    then an AgricolaNotEnoughResources exception is raised.

    Parameters
    ----------
    pastures: list of Pasture instances
      Pastures to add.

    """
    if isinstance(pastures, Pasture):
      pastures = [pastures]
    self._check_spatial_objects(pastures, 'pasture', omit=['stable'])
    Pasture.check_connected_group(self._pastures + pastures)

    existing_fences = Pasture.fences_for_pasture_group(self._pastures)
    new_fences = (
      Pasture.fences_for_pasture_group(pastures) - existing_fences)

    description = "Building {0} pastures".format(len(pastures))
    n_fences = len(new_fences)
    cost = dict(wood=n_fences, fences_avail=n_fences)
    state_change = PlayerStateChange(description, cost=cost)
    state_change.check_and_apply(self)

    self._pastures.extend(pastures)
    for p in pastures:
      self.trigger_event('build_pasture', pasture=p)

  def build_stables(self, spaces, unit_cost):
    if isinstance(spaces, int):
      spaces = [spaces]
    stables = [Stable(s) for s in spaces]

    self._check_spatial_objects(stables, 'stable', omit=['pasture'])
    Stable.check_connected_group(self._stables + stables)

    n_stables = len(spaces)
    description = "Building {0} stables".format(len(spaces))
    cost = dict(wood=unit_cost*n_stables, stables_avail=n_stables)
    state_change = PlayerStateChange(description, cost=cost)
    state_change.check_and_apply(self)

    self._stables.extend(stables)

  def _check_animal_capacity(self, animal_counts, n_added, name):
    animal_counts = sorted(animal_counts)
    capacities = [1] * (self.n_free_stables + 1)

    pasture_capacities = [
      p.capacity() + self.pasture_capacity_modifier for p in self._pastures]

    capacities.extend(pasture_capacities)

    multiset = Counter(capacities)
    if not multiset_satisfy(sorted(animal_counts), multiset):
      raise AgricolaNotEnoughResources(
        "Adding {0} {1}, but player "
        "has insufficient animal capacity.".format(n_added, name))

  def plow_fields(self, spaces):
    if isinstance(spaces[0], int):
      spaces = [spaces]
    fields = [Field(s) for s in spaces]

    self._check_spatial_objects(fields, 'field')
    Field.check_connected_group(self._fields + fields)

    self._fields.extend(fields)

  def sow(self, n_grain, n_veg):
    description = "Sowing {0} grain and {1} veg".format(n_grain, n_veg)
    cost = dict(grain=n_grain, veg=n_veg)
    prereq = dict(empty_fields=n_grain+n_veg)
    state_change = PlayerStateChange(description, cost=cost, prereq=prereq)
    state_change.check_and_apply(self)

    empty_fields = (f for f in self._fields if f.is_empty())

    for g in range(n_grain):
      next(empty_fields).plant_grain()

    for v in range(n_veg):
      next(empty_fields).plant_veg()

  def bake_bread(self, n):
    if n > len(self.bread_rates) - 1 and self.bread_rates[-1] == 0:
      raise AgricolaPoorlyFormed()
    bread_rates = self.bread_rates[:-1][:n]
    n_left = max(n - len(bread_rates), 0)
    bread_rates.extend([self.bread_rates[-1]] * n_left)
    food_gained = sum(bread_rates)

    description = "Baking bread {0} times for {1} food".format(n, food_gained)
    cost = dict(grain=n)
    change = dict(food=food_gained)
    state_change = PlayerStateChange(description, cost=cost, change=change)
    state_change.check_and_apply(self)

  def cook_food(self, counts):
    """
    Parameters
    ----------
    counts: dict (resource_type -> count)

    """
    description = "Cooking food"

    food_gained = 0
    for resource, count in counts.items():
      food_gained += self.cooking_rates[resource]

    cost = counts.copy()
    change = dict(food=food_gained)

    state_change = PlayerStateChange(description, cost=cost, change=change)
    state_change.check_and_apply(self)

  def play_occupation(self, occupation, game):
    occupation.check_and_apply(self)

    self.hand['occupations'].remove(occupation)
    self.occupations.append(occupation)

  def play_minor_improvement(self, improvement, game):
    improvement.check_and_apply(self)

    self.hand['minor_improvements'].remove(improvement)
    self.minor_improvements.append(improvement)

  def play_major_improvement(self, improvement, game):
    improvement.check_and_apply(self)

    self.major_improvements.append(improvement)

  def get_state_dict(self):
    resources = {}
    for key in 'food wood clay stone reed sheep boar cattle grain veg'.split(' '):
      resources[key] = getattr(self, key)
    
    board = []
    room_spaces = set(self.room_spaces)
    stable_spaces = set(self.stable_spaces)
    field_spaces = set(self.field_spaces)

    for i in range(self.shape[0]):
      board_row = []
      for j in range(self.shape[1]):
        board_space = {}
        space = i, j
        if space in room_spaces:
          board_space = {
            "object_type": "wooden_hut"
          }
        elif space in stable_spaces:
          board_space = {
            "object_type": "stable"
          }
        elif space in field_spaces:
          board_space = {
            "object_type": "field"
          }          
          for field in self._fields:
            if field.space == space:
              if field.n_items >= 1:
                board_space["item_count"] = field.n_items
                board_space["kind"] = field.kind
                break
        board_row.append(board_space)
      board.append(board_row)

    played_improvements = list(map(lambda card: {"improvement_id": card.name}, self.minor_improvements + self.major_improvements))
    hand_improvements = list(map(lambda card: card.name, self.hand["minor_improvements"]))
    played_occupations = list(map(lambda card: {"occupation_id": card.name}, self.occupations))
    hand_occupations = list(map(lambda card: card.name, self.hand["occupations"]))

    # TODO set proper family type
    # TODO set newborn
    families = []
    
    for i in range(self.turn_left):
      families.append({
        "family_type": "in_house",
        "newborn": False
      })
    for i in range(self.people - self.turn_left):
      families.append({
        "family_type": "used",
        "newborn": False
      })

    print(self._pastures)
    pasture_state = list(map(lambda pasture: list(map(lambda space: (space[1], space[0]), pasture.spaces)), self._pastures))

    fences_state = list(map(lambda fence: list(map(lambda point: (point[1], point[0]), fence)), self.fences))

    print("=--=--=--=-=-=--=-=-=--=")
    print(pasture_state)

    return {
      "player_id": int(self.name),
      "resources": resources,
      "round_resources": self.futures,
      "board": board,
      "pastures": pasture_state,
      "played_improvements": played_improvements,
      "hand_improvements": hand_improvements,
      "played_occupations": played_occupations,
      "hand_occupations": hand_occupations,
      "families": families,
      "score": self.score(),
      "fences": fences_state,
      "begging_cards": self.begging_cards
    }

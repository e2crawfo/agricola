import numpy as np
import networkx as nx
import itertools
from collections import OrderedDict, Counter
import abc
from future.utils import with_metaclass, iteritems

from agricola.utils import (
    multiset_satisfy, draw_grid, index_check, orthog_adjacent)
from agricola import (
    AgricolaNotEnoughResources, AgricolaLogicError,
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
        for s in self.spaces:
            index_check(s, shape)

    def overlaps(self, other):
        return bool(self.spaces & other.spaces)

    def __contains__(self, space):
        return space in self.spaces

    def spaces(self):
        return self.spaces

    @staticmethod
    def orthog_graph(objects, require_connected=True):
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
                    "Group of SpatialObjects {0} does not form a connected region.".format(s))
        return G

    @staticmethod
    def check_connected_group(objects):
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


class AnimalPen(object):
    @abc.abstractmethod
    def capacity(self):
        return 0


class Stable(SingleSpaceObject, AnimalPen):
    def capacity(self):
        return 1


class Pasture(SpatialObject, AnimalPen):
    def __init__(self, spaces):
        if isinstance(spaces[0], int):
            spaces = [spaces]
        self.spaces = list(set(spaces))

        self.n_stables = 0

        fences = []
        for s in spaces:
            fences.append(((s[0], s[1]), (s[0], s[1]+1)))  # Top
            fences.append(((s[0], s[1]+1), (s[0]+1, s[1]+1)))  # Right
            fences.append(((s[0]+1, s[1]), (s[0]+1, s[1]+1)))  # Bottom
            fences.append(((s[0], s[1]), (s[0]+1, s[1])))  # Left

        counts = Counter(fences)
        self._fences = [f for f, c in iteritems(counts) if c == 1]

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
        return self.n_spaces * 2**(self.n_stables)


RESOURCE_TYPES = ('food wood clay stone reed sheep boar cattle grain veg '
                  'pastures fences fences_avail stables fenced_stables free_stables stables_avail '
                  'rooms people people_avail grain_fields veg_fields empty_fields fields '
                  'empty_spaces used_spaces')
RESOURCE_TYPES = RESOURCE_TYPES.split(' ')


class PlayerStateChange(object):
    """ Encapsulates a change to a Player object.

    Parameters
    ----------
    description: str
        Textual description of the change to effect.
    cost: dict (str -> int)
        Dictionary mapping from resource names to integers
        specifying the amount of that resource required before applying
        this state change. This argument can be omitted.
    change: dict (str -> int) (optional)
        Dictionary mapping from resource names to integers
        specifying the delta to be applied for that resource. This
        argument can be omitted, in which case this object simply
        checks that the supplied costs are satisfied.

    """
    def __init__(self, description, cost=None, change=None):
        self.description = description
        self.cost = cost or {}
        for k, v in cost:
            if k not in RESOURCE_TYPES:
                raise AgricolaLogicError(
                    "Malformed PlayerStateChange object. "
                    "{0} is not a valid resource type.".format(k))
        self.change = change or {}

    def check_and_apply(self, player):
        for key, val in iteritems(self.cost):
            if getattr(player, key) < self.cost[key]:
                raise AgricolaNotEnoughResources(self._error_message(player))

        for k, v in iteritems(self.change):
            player.k += v

    def _error_message(self, player):
        s = [self.description + ' requires']
        pairs = list(iteritems(self.cost))
        n_pairs = len(pairs)

        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("{0} {1},".format(pairs[-1][1], pairs[-1][0]))

        s.append("but player only has")
        for i, (k, v) in enumerate(pairs):
            s.append("{0} {1},".format(v, getattr(player, k)))
        if n_pairs > 1:
            s.append("and")
        s.append("{0} {1}.".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s)


class Player(object):
    # TODO: Some resources are defined explicitly, others are defined through properties that
    # check the status indirectly.

    # TODO: In the constructor, just set all self attributes without doing checks. Then at the end, call a function
    # which checks that constraints are satisfied.

    # TODO: implement harvest. A bit tough because player harvests veg, then has to make a decision about whether to cook it or not (or eat the grain raw).

    # TODO: handle babies vs people.

    # TODO: handle case where people build pastures on top of already existing pastures, e.g. by adding fences inside an existing pasture.

    # TODO: Restrict when and how many times cooking can be
    # done (e.g. joinery (wood to food) can only be done once per harvest).
    def __init__(
            self, shape=None, house_type='wood', rooms=None, fields=None, stables=None, pastures=None,
            food=0, wood=0, clay=0, stone=0, reed=0,
            sheep=0, boar=0, cattle=0, grain=0, veg=0,
            people=2, people_avail=3, fences_avail=15, stables_avail=4):

        resources = dict(
            food=food, wood=wood, clay=clay, stone=stone, reed=reed,
            sheep=sheep, boar=boar, cattle=cattle, grain=grain, veg=veg)
        for k, v in iteritems(resources):
            setattr(self, k, v)

        if shape is None:
            shape = (3, 5)
        self.shape = shape

        self.house_type = house_type
        if rooms is None:
            rooms = [Room((0, 0)), Room((0, 1))]

        self._rooms = rooms or []
        self.people = people
        self.people_avail = people_avail

        self._pastures = pastures or []
        self.fences_avail = fences_avail
        self._stables = stables or []
        self.stables_avail = stables_avail

        self._fields = fields or []

        self.occupations = []
        self.minor_improvements = []
        self.major_improvements = []

        self.house_progression = ['wood', 'clay', 'stone']
        self.room_cost = 5

        # The last rate can be applied infinitely many times during a turn.
        self.bread_rates = [0]

        self.cooking_rates = dict(
            grain=1, veg=1, sheep=0, boar=0, cattle=0, wood=0, clay=0, reed=0)

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

    def __str__(self):
        s = "<Player\n\n"
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
        s += draw_grid(grid, (3, 4), self.fences)

        for key in RESOURCE_TYPES:
            s += "\n{0}: {1}".format(key, getattr(self, key))
        s += "\nSCORE: {0}".format(self.score())
        s += "\n>"
        return s

    def score(self):
        return 0

    def harvest(self):
        pass

    def _check_spatial_objects(self, objects, name, omit=None):
        omit = omit or []
        if isinstance(objects, SpatialObject):
            objects = [objects]

        for o in objects:
            o.index_check(self.shape)

        spaces = []
        for o in objects:
            spaces.extend(o.spaces)
        counts = Counter(spaces)
        for k, v in iteritems(counts):
            if v > 1:
                raise AgricolaImpossible(
                    "Trying to add two {0}s that "
                    "overlap at space {1}.".format(name, k))

        for object_type, objects in iteritems(self.occupied):
            if object_type not in omit:
                for space in spaces:
                    if any(space in o for o in objects):
                        raise AgricolaImpossible(
                            "Trying to place a {0} at space {1} where "
                            "a {2} already exists.".format(
                                name, space, object_type))

    def add_people(self, n=1):
        self.people += n

    def add_food(self, n=1):
        self.food += n

    def add_wood(self, n=1):
        self.wood += n

    def add_clay(self, n=1):
        self.clay += n

    def add_stone(self, n=1):
        self.stone += n

    def add_reed(self, n=1):
        self.reed += n

    def add_sheep(self, n=1):
        animal_counts = (self.n_sheep + n, self.n_boar, self.n_cattle)
        self._check_animal_capacity(animal_counts, n, 'sheep')
        self.sheep += n

    def add_boar(self, n=1):
        animal_counts = (self.n_sheep, self.n_boar + n, self.n_cattle)
        self._check_animal_capacity(animal_counts, n, 'boar')
        self.boar += n

    def add_cattle(self, n=1):
        animal_counts = (self.n_sheep, self.n_boar, self.n_cattle + n)
        self._check_animal_capacity(animal_counts, n, 'cattle')
        self.cattle += n

    def add_grain(self, n=1):
        self.grain += n

    def add_veg(self, n=1):
        self.veg += n

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

    def upgrade_house(self, material):
        # TODO: make use of ``material`` arg, for instances where the player
        # has multiple ways to upgrade their house - eg upgrading directly to stone.
        try:
            idx = self.house_progression.index(self.house_type) + 1
            material_required = self.house_progression[idx]
        except KeyError:
            raise

        description = "Upgrading house from {0} to {1}".format(self.house_type, material_required)
        cost = {self.material_required: self.n_rooms, 'reed': 1}
        state_change = PlayerStateChange(description, cost=cost)
        state_change.check_and_apply(self)

        self.house_type = material_required

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
        for p in pastures:
            self._check_spatial_objects(p, 'pasture', omit=['stable'])
        Pasture.check_connected_group(self._pastures + pastures)

        existing_fences = Pasture.fences_for_pasture_group(self._pastures)
        new_fences = (
            Pasture.fences_for_pasture_group(pastures) - existing_fences)

        description = "Building {0} pastures".format(len(pastures))
        n_fences = len(new_fences)
        state_change = PlayerStateChange(description, cost=dict(wood=n_fences, fences_avail=n_fences))
        state_change.check_and_apply(self)

        self._pastures = self._pastures + pastures

    def build_stables(self, spaces, unit_cost):
        if isinstance(spaces[0], int):
            spaces = [spaces]
        stables = [Stable(s) for s in spaces]

        self._check_spatial_objects(stables, 'stable', omit=['pasture'])
        Stable.check_connected_group(self._stables + stables)

        n_stables = len(spaces)
        description = "Building {0} stables".format(len(spaces))
        state_change = PlayerStateChange(description, cost=dict(wood=unit_cost*n_stables, stables_avail=-n_stables))
        state_change.check_and_apply(self)

        self._stables.extend(stables)

    def _check_animal_capacity(self, animal_counts, n_added, name):
        animal_counts = sorted(animal_counts)
        capacities = [1] * (self.n_free_stables + 1)
        capacities.extend(p.capacity() for p in self._pastures)

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
        state_change = PlayerStateChange(description, cost=dict(grain=n_grain, veg=n_veg, empty_fields=n_grain+n_veg))
        state_change.check_and_apply(self)

        empty_fields = (f for f in self._fields if f.is_empty())

        for g in range(n_grain):
            next(empty_fields).plant_grain()

        for v in range(n_veg):
            next(empty_fields).plant_veg()

    def bake_bread(self, n):
        if n > len(self.bread_rates-1) and self.bread_rates[-1] == 0:
            raise AgricolaPoorlyFormed()
        bread_rates = self.bread_rates[:-1][:n]
        n_left = max(n - len(bread_rates), 0)
        bread_rates.extend([self.bread_rates[-1]] * n_left)
        n_food = itertools.product(bread_rates)

        description = "Baking bread {0} times".format(n)
        state_change = PlayerStateChange(description, cost=dict(grain=n), change=dict(food=n_food))
        state_change.check_and_apply(self)

    def cook_food(self, counts):
        """
        Parameters
        ----------
        counts: dict (resource_type -> count)

        """
        description = "Cooking food"
        change = {'food': 0}
        for r, c in iteritems(counts):
            change[r] = -c
            change['food'] += self.cooking_rates[r]

        state_change = PlayerStateChange(description, cost=counts, change=change)
        state_change.check_and_apply(self)

    def add_occupation(self, occupation):
        occupation.check_and_apply(self)
        self.occupations.append(occupation)

    def add_minor_improvement(self, improvement):
        improvement.check_and_apply(self)
        self.minor_improvements.append(improvement)

    def add_major_improvement(self, improvement):
        improvement.check_and_apply(self)
        self.major_improvements.append(improvement)

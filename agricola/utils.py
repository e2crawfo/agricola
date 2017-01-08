import numpy as np
import numbers
import itertools
from collections import OrderedDict, Counter
from future.utils import iteritems


def check_random_state(seed):
    """ Taken from sklearn.

    Turn seed into a np.random.RandomState instance
    If seed is None, return the RandomState singleton used by np.random.
    If seed is an int, return a new RandomState instance seeded with seed.
    If seed is already a RandomState instance, return it.
    Otherwise raise ValueError.

    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, (numbers.Integral, np.integer)):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError('%r cannot be used to seed a numpy.random.RandomState'
                     ' instance' % seed)


def orthog_adjacent(a, b):
    a, b = np.array(a), np.array(b)
    abs_diff = np.abs(a - b)
    return (np.count_nonzero(abs_diff) == 1) and (abs_diff.sum() == 1)


def index_check(idx, shape):
    idx = np.array(idx)
    if any(idx < 0) or any(idx >= shape):
        raise IndexError("idx: {0}, shape: {1}".format(idx, shape))


def _fence_loc_to_grid_loc(fence_loc, cell_shape):
    return np.array(fence_loc) * (cell_shape + 1)


def draw_grid(cells, cell_shape, fences=None):
    """
    Parameters
    ----------
    cells: numpy array
        pass
    cell_shape: tuple-like, length=2
        Shape of a cell in *matrix* format (y-idx first).
    fences: list of fences
        Fences to draw (also in matrix format).

    """
    fences = fences or []
    cells = np.array(cells)
    shape = np.array(cells.shape)
    cell_shape = np.array(cell_shape)
    grid_shape = (cell_shape + 1) * shape + 1
    grid = np.tile(np.array(' '), grid_shape)

    h_corners, v_corners = [], []

    for fence in fences:
        diff = np.array(fence[1]) - np.array(fence[0])
        horizontal = diff[1] == 1
        char = '-' if horizontal else '|'
        start = _fence_loc_to_grid_loc(fence[0], cell_shape)
        (h_corners if horizontal else v_corners).append(tuple(start))

        start += diff
        end = start + diff * cell_shape
        (h_corners if horizontal else v_corners).append(tuple(end))

        if horizontal:
            grid[start[0], start[1]:end[1]] = char
        else:
            grid[start[0]:end[0], start[1]] = char

    h_corner_count = Counter(h_corners)
    for corner, count in iteritems(h_corner_count):
        if count > 1:
            grid[corner] = '-'

    v_corner_count = Counter(v_corners)
    for corner, count in iteritems(v_corner_count):
        if count > 1:
            grid[corner] = '|'

    cross_corners = set(h_corners) & set(v_corners)
    for corner in cross_corners:
        grid[corner] = '+'

    for i in range(shape[0]):
        for j in range(shape[1]):
            upper_left = 1 + np.array((i, j)) * (1 + cell_shape)
            bottom_right = upper_left + cell_shape
            grid[upper_left[0]:bottom_right[0], upper_left[1]:bottom_right[1]] = cells[i, j]

    return '\n'.join(''.join(c for c in row) for row in grid)


def multiset_subtract(a, b):
    a_copy = a.copy()
    for k, v in iteritems(b):
        if k in a_copy:
            a_copy[k] -= v
            a_copy[k] = max(0, a_copy[k])
    return a_copy


def multiset_weight(a):
    return sum([k * v for k, v in iteritems(a)])


def multiset_satisfy(constraints, multiset):
    """
    Check whether there is (a partition of the multiset
    whose size is equal to the length of ``constraints``) such that
    the total weight of each component of the partition is at least big
    as its corresponding entry in ``constraints``.

    Parameters
    ----------
    constraints: list of int
        The constraints.
    multiset: dict (keytype -> int)
        The multiset.

    """
    if not constraints:
        return True

    if len(constraints) == 1:
        return multiset_weight(multiset) >= constraints[0]

    # Easy check.
    if multiset_weight(multiset) < sum(constraints):
        return False

    multiset = OrderedDict(multiset)
    for counts in itertools.product(*[range(v+1) for k, v in iteritems(multiset)]):
        submultiset = {k: count for k, count in zip(multiset, counts)}
        weight = multiset_weight(submultiset)
        if weight < constraints[0]:
            continue

        remaining = multiset_subtract(multiset, submultiset)

        success = multiset_satisfy(constraints[1:], remaining)
        if success:
            return True

    return False

import pytest
from agricola import (
    AgricolaLogicError, AgricolaNotEnoughResources, AgricolaImpossible)
from agricola.player import Player, Pasture
from agricola.utils import multiset_satisfy


def test_pasture_intraconn():
    """ Test that individual Pastures are forced to be connected. """
    Pasture([(0, 0)])
    Pasture([(0, 0), (1, 0)])
    Pasture([(0, 0), (1, 0), (2, 0)])
    Pasture([(0, 0), (1, 0), (0, 1)])
    Pasture([(0, 0), (1, 0), (0, 1), (1, 1)])

    with pytest.raises(AgricolaLogicError):
        Pasture([(0, 0), (0, 2)])

    with pytest.raises(AgricolaLogicError):
        Pasture([(0, 0), (2, 0)])

    with pytest.raises(AgricolaLogicError):
        Pasture([(0, 0), (1, 1)])

    with pytest.raises(AgricolaLogicError):
        Pasture([(0, 0), (1, 1), (2, 1)])


def test_pasture_overlap():
    """ Test that pastures are not allowed to overlap with one another. """
    a = Pasture([(0, 1)])
    b = Pasture([(0, 1), (0, 2)])
    c = Pasture([(0, 2), (0, 3)])

    assert a.overlaps(b)
    assert b.overlaps(a)

    assert b.overlaps(c)
    assert c.overlaps(b)

    assert not a.overlaps(c)
    assert not c.overlaps(a)

    p = Player("p0", wood=20)
    p.build_pastures(a)
    p.build_pastures(c)

    p = Player("p0", wood=20)
    p.build_pastures(c)
    p.build_pastures(a)

    p = Player("p0", wood=20)
    p.build_pastures([a, c])

    p = Player("p0", wood=20)
    p.build_pastures([c, a])

    p = Player("p0", wood=20)
    p.build_pastures(b)

    p = Player("p0", wood=20)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures([a, b])

    p = Player("p0", wood=20)
    p.build_pastures(a)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(b)

    p = Player("p0", wood=20)
    p.build_pastures(b)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(a)

    p = Player("p0", wood=20)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures([c, b])

    p = Player("p0", wood=20)
    p.build_pastures(c)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(b)

    p = Player("p0", wood=20)
    p.build_pastures(b)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(c)


def test_pasture_bounds():
    """ Test that Pastures are forced to be built within the bounds of the board. """
    p = Player("p0", wood=20, shape=(2, 2), rooms=[])
    pastures = [Pasture([(0, 0), (1, 0)]), Pasture([(0, 1), (1, 1)])]
    p.build_pastures(pastures)

    p = Player("p0", wood=20, shape=(2, 1), rooms=[])
    with pytest.raises(IndexError):
        p.build_pastures(pastures)


def test_pasture_conflict():
    """ Test that Pastures are not allowed to be built on top of rooms or fields. """
    p = Player("p0", wood=20, rooms=[(0, 0)], fields=[(1, 1)], stables=[(2, 2)])

    with pytest.raises(AgricolaImpossible) as exc_info:
        p.build_pastures(Pasture((0, 0)))
    assert 'room' in str(exc_info.value)

    with pytest.raises(AgricolaImpossible) as exc_info:
        p.build_pastures([Pasture((0, 0)), Pasture((1, 0))])
    assert 'room' in str(exc_info.value)

    with pytest.raises(AgricolaImpossible) as exc_info:
        p.build_pastures(Pasture((1, 1)))
    assert 'field' in str(exc_info.value)

    with pytest.raises(AgricolaImpossible) as exc_info:
        p.build_pastures([Pasture((1, 1)), Pasture((2, 1))])
    assert 'field' in str(exc_info.value)


def test_pasture_intercon():
    """ Test that Pastures are forced to be adjacent to one another. """
    a = Pasture((0, 1))
    b = Pasture((1, 1))
    c = Pasture((1, 2))
    d = Pasture([(0, 3), (0, 4)])
    e = Pasture((0, 2))
    f = Pasture([(1, 2), (1, 3)])

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(a)
    p.build_pastures(b)
    p.build_pastures(c)

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures([a, b, c])

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures([a, b])
    p.build_pastures(c)

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures([b, c])
    p.build_pastures(a)

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(b)
    p.build_pastures([a, c])

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(c)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(a)

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(a)
    with pytest.raises(AgricolaLogicError):
        p.build_pastures(c)

    p = Player("p0", wood=20, rooms=[])
    with pytest.raises(AgricolaLogicError):
        p.build_pastures([a, c])

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(d)
    p.build_pastures(e)

    p = Player("p0", wood=20, rooms=[])
    p.build_pastures(d)
    p.build_pastures(f)

    p = Player("p0", wood=20, fences_avail=17, rooms=[])
    p.build_pastures([a, b, c, d, e])

    p = Player("p0", wood=20, fences_avail=17, rooms=[])
    with pytest.raises(AgricolaLogicError):
        p.build_pastures([a, b, c, d])


def test_pasture_cost():
    """ Test that costs for building Pastures are evaluated correctly. """
    a = Pasture((0, 1))
    b = Pasture((1, 1))
    c = Pasture((1, 2))
    d = Pasture([(0, 3), (0, 4)])
    e = Pasture((0, 2))
    f = Pasture([(1, 2), (1, 3)])

    player = Player("p0", wood=0, rooms=[])
    for p in [a, b, c, d, e, f]:
        with pytest.raises(AgricolaNotEnoughResources):
            player.build_pastures(p)

    player = Player("p0", wood=4, rooms=[])
    player.build_pastures(a)
    assert player.wood == 0

    player = Player("p0", wood=4, rooms=[])
    player.build_pastures(b)
    assert player.wood == 0

    player = Player("p0", wood=4, rooms=[])
    player.build_pastures(c)
    assert player.wood == 0

    player = Player("p0", wood=6, rooms=[])
    player.build_pastures(d)
    assert player.wood == 0

    player = Player("p0", wood=4, rooms=[])
    player.build_pastures(e)
    assert player.wood == 0

    player = Player("p0", wood=6, rooms=[])
    player.build_pastures(f)
    assert player.wood == 0

    player = Player("p0", wood=6, rooms=[])
    player.build_pastures(f)
    assert player.wood == 0

    player = Player("p0", wood=10, rooms=[])
    player.build_pastures([a, b, c])
    assert player.wood == 0

    player = Player("p0", wood=11, rooms=[])
    player.build_pastures([d, f])
    assert player.wood == 0

    player = Player("p0", wood=9, rooms=[])
    player.build_pastures([d, e])
    assert player.wood == 0

    player = Player("p0", wood=13, rooms=[])
    player.build_pastures([d, e, f])
    assert player.wood == 0


def test_pasture_fence_use():
    """ Test that pastures cannot be build if player possesses
        insufficient fences.
    """
    a = Pasture((0, 1))
    b = Pasture((1, 1))
    c = Pasture((1, 2))
    d = Pasture([(0, 3), (0, 4)])
    e = Pasture((0, 2))
    f = Pasture([(1, 2), (1, 3)])

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    player.build_pastures(a)

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    player.build_pastures(b)

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    player.build_pastures(c)

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    player.build_pastures(e)

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    with pytest.raises(AgricolaNotEnoughResources) as exc_info:
        player.build_pastures(d)
    assert '4 fences_avail' in str(exc_info.value)

    player = Player("p0", wood=20, fences_avail=4, rooms=[])
    with pytest.raises(AgricolaNotEnoughResources) as exc_info:
        player.build_pastures(f)
    assert '4 fences_avail' in str(exc_info.value)


def test_multiset_satisfy():
    multiset = {2: 1, 1: 1}
    constraints = [2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(sat)

    multiset = {2: 2, 1: 1}
    constraints = [2, 2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(sat)

    multiset = {2: 3, 1: 4}
    constraints = [3, 2, 2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(sat)

    multiset = {2: 3, 1: 4}
    constraints = [3, 2, 2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(sat)

    multiset = {6: 1, 1: 4}
    constraints = [3, 2, 2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(not sat)

    multiset = {6: 1, 1: 5}
    constraints = [3, 2, 2, 1]
    sat = multiset_satisfy(constraints, multiset)
    assert(sat)

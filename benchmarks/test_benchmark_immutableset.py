import pytest
import random

from immutablecollections import ImmutableDict, ImmutableSet

empty_tuple = ()
empty_list = []
empty_set = set()
empty_frozenset = frozenset()

small_tuple = (3, 1, 2)
small_list = [3, 1, 2]
small_set = set(small_tuple)
small_frozen_set = set(small_list)

rand = random.Random(0)

big_list = list(range(10000))
rand.shuffle(big_list)
big_tuple = tuple(big_list)
big_set = set(big_list)
big_frozen_set = frozenset(big_list)

input_types = ImmutableDict.of((
    ('empty set', empty_set),
    ('empty frozenset', empty_frozenset),
    ('empty tuple', empty_tuple),
    ('empty list', empty_list),
    ('small set', small_set),
     ('small frozenset', small_frozen_set),
     ('small tuple', small_tuple),
     ('small list', small_list),
    ('big set', big_set),
    ('big frozenset', big_frozen_set),
    ('big tuple', big_tuple),
    ('big list', big_list)
))

constructors = ImmutableDict.of((
    ('set', set),
    ('frozenset', frozenset),
    ('ImmutableSet', ImmutableSet.of),
))


@pytest.mark.parametrize('constructor', constructors.items())
@pytest.mark.parametrize('source', input_types.items())
def test_perf(constructor, source, benchmark):
    benchmark.name = constructor[0]
    benchmark.group = f'Creating from {source[0]}'
    benchmark(constructor[1], source[1])

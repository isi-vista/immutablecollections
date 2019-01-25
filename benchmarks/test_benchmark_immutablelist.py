import random
import pytest
from immutablecollections import ImmutableList
from immutablecollections import ImmutableDict, ImmutableList

empty_tuple = ()
empty_list = []

small_tuple = (3, 1, 2)
small_list = [3, 1, 2]

rand = random.Random(0)

big_list = list(range(10000))
rand.shuffle(big_list)
big_tuple = tuple(big_list)

input_types = ImmutableDict.of((
    ('empty tuple', empty_tuple),
    ('empty list', empty_list),
     ('small tuple', small_tuple),
     ('small list', small_list),
    ('big tuple', big_tuple),
    ('big list', big_list)
))

constructors = ImmutableDict.of((
    ('list', list),
    ('tuple', tuple),
    ('ImmutableList', ImmutableList.of),
))


@pytest.mark.parametrize('constructor', constructors.items())
@pytest.mark.parametrize('source', input_types.items())
def test_perf(constructor, source, benchmark):
    benchmark.name = constructor[0]
    benchmark.group = f'Creating from {source[0]}'
    benchmark(constructor[1], source[1])

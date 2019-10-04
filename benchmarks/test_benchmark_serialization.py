# pylint: disable=invalid-name
import random
from pickle import dumps

import pytest

from immutablecollections import immutabledict, immutableset

empty_tuple = ()
empty_list = []
empty_set = set()
empty_dict = {}

small_tuple = (3, 1, 2)
small_list = [3, 1, 2]
small_set = set([3, 1, 2])
small_dict = {"a": 3, "b": 1, "c": 2}

rand = random.Random(0)

big_dim = int(1e5)

big_list = list(range(big_dim))
rand.shuffle(big_list)
big_tuple = tuple(big_list)
big_set = set(big_tuple)
rand.shuffle(big_list)
big_dict = dict(zip(big_list, big_tuple))

empty_immutableset = immutableset()
empty_immutabledict = immutabledict()
small_immutableset = immutableset(small_tuple)
small_immutabledict = immutabledict(small_dict)
big_immutableset = immutableset(big_tuple)
big_immutabledict = immutabledict(big_dict)


input_types = immutabledict(
    (
        ("empty tuple", empty_tuple),
        ("empty list", empty_list),
        ("empty set", empty_set),
        ("empty immutableset", empty_immutableset),
        ("empty dict", empty_dict),
        ("empty immutabledict", empty_immutabledict),
        ("small tuple", small_tuple),
        ("small list", small_list),
        ("small set", small_set),
        ("small immutableset", small_immutableset),
        ("small dict", small_dict),
        ("small immutabledict", small_immutabledict),
        ("big tuple", big_tuple),
        ("big list", big_list),
        ("big set", big_set),
        ("big immutableset", big_immutableset),
        ("big dict", big_dict),
        ("big immutabledict", big_immutabledict),
    )
)


def serialize(obj):
    return dumps(obj)


@pytest.mark.parametrize("source", input_types.items())
def test_serialization(source, benchmark):
    benchmark.name = source[0]
    benchmark.group = "Serialization"
    benchmark(serialize, source[1])

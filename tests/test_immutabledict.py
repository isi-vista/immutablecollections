import pickle
from collections.abc import Mapping
from unittest import TestCase

from immutablecollections import (
    ImmutableDict,
    immutabledict,
    immutabledict_from_unique_keys,
)

from pytest import raises


class TestImmutableDict(TestCase):
    def test_empty(self):
        empty = immutabledict()
        self.assertEqual(0, len(empty))
        empty2 = immutabledict([])
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)

    def test_empty_singleton(self):
        empty1 = immutabledict()
        empty2 = immutabledict()
        self.assertIs(empty1, empty2)
        empty4 = immutabledict([])
        self.assertIs(empty1, empty4)

    def test_basic(self):
        source = {"a": 1}
        dict1 = immutabledict(source)
        self.assertEqual(dict(dict1), source)
        self.assertEqual(len(dict1), 1)
        self.assertEqual(dict1["a"], 1)

    def test_return_identical_immutable(self):
        dict1 = immutabledict({"a": 1})
        dict2 = immutabledict(dict1)
        self.assertIs(dict1, dict2)

    def test_put_all_iterable(self):
        dict1 = immutabledict({"a": 1})
        dict2 = dict1.modified_copy_builder().put_all([("c", "d"), ("e", "f")]).build()
        self.assertEqual(immutabledict({"a": 1, "c": "d", "e": "f"}), dict2)

    def test_put_all_mapping(self):
        dict1 = immutabledict({"a": 1})
        dict2 = dict1.modified_copy_builder().put_all({"c": "d", "e": "f"}).build()
        self.assertEqual(immutabledict({"a": 1, "c": "d", "e": "f"}), dict2)

    def test_hash_eq(self):
        dict1 = immutabledict({"a": 1, "b": 2})
        dict2 = immutabledict({"b": 2, "a": 1})
        dict3 = immutabledict({"a": 1})

        # Order of original dict does not matter
        self.assertEqual(dict1, dict2)
        self.assertNotEqual(dict1, dict3)

        val = object()
        d = {dict1: val}
        self.assertEqual(d[dict2], val)
        self.assertEqual(hash(dict2), hash(dict1))
        self.assertTrue(dict3 not in d)

        # test comparison with regular dicts
        f = {"foo": "bar", "oof": "rab"}
        immutable_f = immutabledict(f)
        self.assertEqual(immutable_f, f)
        self.assertEqual(f, immutable_f)

        # ensure ImmutableDict is hashable
        hash(immutable_f)

    def test_immutable(self):
        source = {"a": 1}
        dict1 = immutabledict(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            dict1.update({"b": 2})
        # Update doesn't affect original
        source.update({"b": 2})
        self.assertNotEqual(immutabledict(source), dict1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableDict({"a": 1})

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            immutabledict(7)

    def test_items_init(self):
        source = {"a": 1}
        self.assertEqual(immutabledict(source.items()), immutabledict(source))

    def test_unhashable_key(self):
        # Cannot create using unhashable keys
        source = [([1, 2, 3], 1)]
        with self.assertRaises(TypeError):
            immutabledict(source)

    def test_unhashable_value(self):
        source = {1: [1, 2, 3]}
        # Can create with unhashable values, but cannot hash the resulting object
        dict1 = immutabledict(source)
        with self.assertRaises(TypeError):
            hash(dict1)

    def test_isinstance(self):
        dict1 = immutabledict({"a": 1})
        self.assertTrue(isinstance(dict1, Mapping))

    def test_slots(self):
        self.assertFalse(hasattr(immutabledict({"a": 1}), "__dict__"))

    def test_repr(self):
        self.assertEqual("i{1: 2, 3: 4}", repr(immutabledict({1: 2, 3: 4})))

    def test_str(self):
        self.assertEqual("{1: 2, 3: 4}", str(immutabledict({1: 2, 3: 4})))

    def test_index(self):
        # pylint: disable=unnecessary-lambda
        by_length = ImmutableDict.index(["foo", "fooo", "la"], lambda s: len(s))
        self.assertEqual(3, len(by_length))
        self.assertEqual("foo", by_length[3])
        self.assertEqual("fooo", by_length[4])
        self.assertEqual("la", by_length[2])

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source = {"a": 1}
        dict1: Mapping[str, int] = immutabledict(source)
        return dict1["a"]

    def test_pickling(self):
        self.assertEqual(
            pickle.loads(pickle.dumps(immutabledict([(5, "apple"), (2, "banana")]))),
            immutabledict([(5, "apple"), (2, "banana")]),
        )
        self.assertEqual(
            immutabledict([(5, "apple"), (2, "banana")]).__reduce__(),
            (immutabledict, (((5, "apple"), (2, "banana")),)),
        )

    def test_immutabledict_duplication_blocking(self):
        bad = [(7, 8), (9, 10), (7, 11)]
        with self.assertRaises(ValueError):
            immutabledict(bad, forbid_duplicate_keys=True)
        with self.assertRaises(ValueError):
            immutabledict_from_unique_keys(bad)
        with self.assertRaises(ValueError):
            immutabledict((x for x in bad), forbid_duplicate_keys=True)
        with self.assertRaises(ValueError):
            immutabledict_from_unique_keys(x for x in bad)

        good = [(7, 8), (9, 10), (12, 11)]
        immutabledict(good, forbid_duplicate_keys=True)
        immutabledict_from_unique_keys(good)
        immutabledict((x for x in good), forbid_duplicate_keys=True)
        immutabledict_from_unique_keys(x for x in good)

    def test_inverse(self):
        self.assertEqual(
            immutabledict({"foo": "bar", "bar": "bat"}).inverse(),
            immutabledict({"bar": "foo", "bat": "bar"}),
        )

    def test_inverse_non_unique_keys(self):
        with raises(
            ValueError,
            match="forbid_duplicate_keys=True, but some keys occur multiple times in input: .*",
        ):
            immutabledict({"foo": "bar", "bat": "bar"}).inverse()

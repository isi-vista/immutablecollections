from collections.abc import Mapping
from unittest import TestCase

from immutablecollections import ImmutableDict


class TestImmutableDict(TestCase):
    def test_empty(self):
        empty = ImmutableDict.empty()
        self.assertEqual(0, len(empty))
        empty2 = ImmutableDict.of([])
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)
        empty3 = ImmutableDict.builder().build()
        self.assertEqual(0, len(empty3))
        self.assertEqual(empty, empty3)

    def test_empty_singleton(self):
        empty1 = ImmutableDict.empty()
        empty2 = ImmutableDict.empty()
        self.assertIs(empty1, empty2)
        empty3 = ImmutableDict.builder().build()
        self.assertIs(empty1, empty3)
        empty4 = ImmutableDict.of([])
        self.assertIs(empty1, empty4)

    def test_basic(self):
        source = {"a": 1}
        dict1 = ImmutableDict.of(source)
        self.assertEqual(dict(dict1), source)
        self.assertEqual(len(dict1), 1)
        self.assertEqual(dict1["a"], 1)

    def test_return_identical_immutable(self):
        dict1 = ImmutableDict.of({"a": 1})
        dict2 = ImmutableDict.of(dict1)
        self.assertIs(dict1, dict2)

    def test_put_all_iterable(self):
        dict1 = ImmutableDict.of({"a": 1})
        dict2 = dict1.modified_copy_builder().put_all([("c", "d"), ("e", "f")]).build()
        self.assertEqual(ImmutableDict.of({"a": 1, "c": "d", "e": "f"}), dict2)

    def test_put_all_mapping(self):
        dict1 = ImmutableDict.of({"a": 1})
        dict2 = dict1.modified_copy_builder().put_all({"c": "d", "e": "f"}).build()
        self.assertEqual(ImmutableDict.of({"a": 1, "c": "d", "e": "f"}), dict2)

    def test_singleton_empty(self):
        empty = ImmutableDict.empty()
        empty2 = ImmutableDict.empty()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        dict1 = ImmutableDict.of({"a": 1, "b": 2})
        dict2 = ImmutableDict.of({"b": 2, "a": 1})
        dict3 = ImmutableDict.of({"a": 1})

        # Order of original dict does not matter
        self.assertEqual(dict1, dict2)
        self.assertNotEqual(dict1, dict3)

        val = object()
        d = {dict1: val}
        self.assertEqual(d[dict2], val)
        self.assertEqual(hash(dict2), hash(dict1))
        self.assertTrue(dict3 not in d)

    def test_immutable(self):
        source = {"a": 1}
        dict1 = ImmutableDict.of(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            dict1.update({"b": 2})
        # Update doesn't affect original
        source.update({"b": 2})
        self.assertNotEqual(ImmutableDict.of(source), dict1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableDict({"a": 1})

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            ImmutableDict.of(7)

    def test_items_init(self):
        source = {"a": 1}
        self.assertEqual(ImmutableDict.of(source.items()), ImmutableDict.of(source))

    def test_unhashable_key(self):
        # Cannot create using unhashable keys
        source = [([1, 2, 3], 1)]
        with self.assertRaises(TypeError):
            ImmutableDict.of(source)

    def test_unhashable_value(self):
        source = {1: [1, 2, 3]}
        # Can create with unhashable values, but cannot hash the resulting object
        dict1 = ImmutableDict.of(source)
        with self.assertRaises(TypeError):
            hash(dict1)

    def test_isinstance(self):
        dict1 = ImmutableDict.of({"a": 1})
        self.assertTrue(isinstance(dict1, Mapping))

    def test_slots(self):
        self.assertFalse(hasattr(ImmutableDict.of({"a": 1}), "__dict__"))

    def test_repr(self):
        self.assertEqual("i{1: 2, 3: 4}", repr(ImmutableDict.of({1: 2, 3: 4})))

    def test_str(self):
        self.assertEqual("{1: 2, 3: 4}", str(ImmutableDict.of({1: 2, 3: 4})))

    def test_index(self):
        by_length = ImmutableDict.index(["foo", "fooo", "la"], lambda s: len(s))
        self.assertEqual(3, len(by_length))
        self.assertEqual("foo", by_length[3])
        self.assertEqual("fooo", by_length[4])
        self.assertEqual("la", by_length[2])

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source: Mapping[str, int] = {"a": 1}
        dict1 = ImmutableDict.of(source)
        return dict1["a"]

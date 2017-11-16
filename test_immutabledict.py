from collections.abc import Mapping
from unittest import TestCase

from flexnlp.util.immutablecollections import ImmutableDict


class TestImmutableDict(TestCase):

    def test_empty_dict(self):
        empty = ImmutableDict.empty()
        self.assertEqual(dict(empty), {})

    def test_basic(self):
        source = {'a': 1}
        dict1 = ImmutableDict.of(source)
        self.assertEqual(dict(dict1), source)
        self.assertEqual(len(dict1), 1)
        self.assertEqual(dict1['a'], 1)

    def test_return_identical_immutable(self):
        dict1 = ImmutableDict.of({'a': 1})
        dict2 = ImmutableDict.of(dict1)
        self.assertIs(dict1, dict2)

    def test_singleton_empty(self):
        empty = ImmutableDict.empty()
        empty2 = ImmutableDict.empty()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        dict1 = ImmutableDict.of({'a': 1, 'b': 2})
        dict2 = ImmutableDict.of({'b': 2, 'a': 1})
        dict3 = ImmutableDict.of({'a': 1})

        # Order of original dict does not matter
        self.assertEqual(dict1, dict2)
        self.assertNotEqual(dict1, dict3)

        val = object()
        d = {dict1: val}
        self.assertEqual(d[dict2], val)
        self.assertEqual(hash(dict2), hash(dict1))
        self.assertTrue(dict3 not in d)

    def test_immutable(self):
        source = {'a': 1}
        dict1 = ImmutableDict.of(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            dict1.update({'b': 2})
        # Update doesn't affect original
        source.update({'b': 2})
        self.assertNotEqual(ImmutableDict.of(source), dict1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableDict({'a': 1})

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            ImmutableDict.of(7)

    def test_items_init(self):
        source = {'a': 1}
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
        dict1 = ImmutableDict.of({'a': 1})
        self.assertTrue(isinstance(dict1, Mapping))

    def test_slots(self):
        self.assertFalse(hasattr(ImmutableDict.of({'a': 1}), '__dict__'))

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source: Mapping[str, int] = {'a': 1}
        dict1 = ImmutableDict.of(source)
        return dict1['a']

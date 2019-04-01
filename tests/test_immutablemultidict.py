import pickle
from collections import Mapping
from unittest import TestCase

from immutablecollections import (
    ImmutableSet,
    ImmutableSetMultiDict,
    ImmutableListMultiDict,
    immutablesetmultidict,
    immutablelistmultidict,
    immutableset,
)


class TestImmutableSetMultiDict(TestCase):
    def test_empty(self):
        empty = immutablesetmultidict()
        self.assertEqual(0, len(empty))
        empty2 = ImmutableSetMultiDict.of(dict())
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)

    def test_empty_singleton(self):
        empty1 = immutablesetmultidict()
        empty2 = immutablesetmultidict()
        self.assertIs(empty1, empty2)
        empty4 = ImmutableSetMultiDict.of(dict())
        self.assertIs(empty1, empty4)

    def test_set_repr(self):
        self.assertEqual(
            "i{1: {2, 3}, 4: {5, 6}}",
            repr(ImmutableSetMultiDict.of({1: [2, 3], 4: [5, 6]})),
        )

    def test_set_str(self):
        self.assertEqual(
            "{1: {2, 3}, 4: {5, 6}}",
            str(ImmutableSetMultiDict.of({1: [2, 3], 4: [5, 6]})),
        )

    def test_of(self):
        x = ImmutableSetMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertEqual(ImmutableSet.of([2, 3]), x[1])
        y = immutablesetmultidict([(1, 2), (1, 2), (1, 3), (4, 5), (4, 6)])
        self.assertEqual(immutableset([2, 3]), y[1])

    def test_unmodified_copy_builder(self):
        ref: ImmutableSetMultiDict[str, int] = (
            ImmutableSetMultiDict.builder()
            .put("foo", 5)
            .put("bar", 6)
            .put("foo", 4)
            .build()
        )

        self.assertEqual(ref, ref.modified_copy_builder().build())

    def test_modified_copy_builder(self):
        start: ImmutableSetMultiDict[str, int] = (
            ImmutableSetMultiDict.builder()
            .put("foo", 5)
            .put("bar", 6)
            .put("foo", 4)
            .build()
        )
        updated = (
            start.modified_copy_builder()
            .put("bar", 1)
            .put("foo", 7)
            .put("meep", -1)
            .build()
        )

        ref: ImmutableSetMultiDict[str, int] = (
            ImmutableSetMultiDict.builder()
            .put("foo", 5)
            .put("bar", 6)
            .put("foo", 4)
            .put("foo", 7)
            .put("bar", 1)
            .put("meep", -1)
            .build()
        )
        self.assertEqual(ref, updated)

    def test_len(self):
        x = ImmutableSetMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        # note 4, not 5, because two of them are collapsed
        self.assertEqual(4, len(x))
        # len's implementation often does caching, so test it works twice
        self.assertEqual(4, len(x))

    def test_hash(self):
        hash(immutablesetmultidict({1: [2, 2, 3], 4: [5, 6]}))

    def test_inversion(self):
        x = ImmutableSetMultiDict.of({1: [2, 2, 3, 6], 4: [5, 6]})
        # when you start from a set multidict, your inverses as a list
        # and set multidict both contain the same items, since there
        # are no duplicate mappings in the source
        reference_set_based = ImmutableSetMultiDict.of(
            {2: [1], 3: [1], 5: [4], 6: [1, 4]}
        )
        reference_list_based = ImmutableListMultiDict.of(
            {2: [1], 3: [1], 5: [4], 6: [1, 4]}
        )
        self.assertEqual(reference_set_based, x.invert_to_set_multidict())
        self.assertEqual(reference_list_based, x.invert_to_list_multidict())

    def test_pickling(self):
        self.assertEqual(
            pickle.loads(
                pickle.dumps(immutablesetmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]))
            ),
            immutablesetmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]),
        )
        self.assertEqual(
            pickle.loads(pickle.dumps(immutablesetmultidict())), immutablesetmultidict()
        )
        self.assertEqual(
            immutablesetmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]).__reduce__(),
            (immutablesetmultidict, (((1, (2, 2, 3, 6)), (4, (5, 6))),)),
        )
        self.assertEqual(
            immutablesetmultidict().__reduce__(), (immutablesetmultidict, ((),))
        )


class TestImmutableListMultiDict(TestCase):
    def test_empty(self):
        empty = immutablelistmultidict()
        self.assertEqual(0, len(empty))
        empty2 = ImmutableListMultiDict.of(dict())
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)

    def test_empty_singleton(self):
        empty1 = immutablelistmultidict()
        empty2 = immutablelistmultidict()
        self.assertIs(empty1, empty2)
        empty4 = ImmutableListMultiDict.of(dict())
        self.assertIs(empty1, empty4)

    def test_of(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertEqual([2, 2, 3], list(x[1]))
        y = immutablelistmultidict([(1, 2), (1, 2), (1, 3), (4, 5), (4, 6)])
        self.assertEqual([2, 2, 3], list(y[1]))

    def test_repr(self):
        self.assertEqual(
            "i{1: (2, 2, 3)}", repr(ImmutableListMultiDict.of({1: [2, 2, 3]}))
        )

    def test_str(self):
        self.assertEqual("{1: (2, 2, 3)}", str(ImmutableListMultiDict.of({1: [2, 2, 3]})))

    def test_hash(self):
        hash(immutablelistmultidict({1: [2, 2, 3], 4: [5, 6]}))

    def test_immutable_keys(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        # TypeError: '_ImmutableDictBackedImmutableListMultiDict' object does not support item
        # assignment
        with self.assertRaises(TypeError):
            # noinspection PyUnresolvedReferences
            x[20] = [1, 2]

    def test_immutable_values(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        # AttributeError: '_TupleBackedImmutableList' object has no attribute 'append'
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            x[1].append(7)
        # TypeError: '_TupleBackedImmutableList' object does not support item assignment
        with self.assertRaises(TypeError):
            # noinspection PyUnresolvedReferences
            x[1][0] = 7

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableListMultiDict(dict())

    def test_isinstance(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertFalse(isinstance(x, Mapping))
        self.assertTrue(isinstance(x.as_dict(), Mapping))

    def test_slots(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertFalse(hasattr(x, "__dict__"))

    def test_builder(self):
        b: ImmutableListMultiDict.Builder[str, int] = ImmutableListMultiDict.builder()
        b.put("key", 1)
        b.put_all({"key": [3, 2, 1]})
        x = b.build()
        self.assertEqual([1, 3, 2, 1], list(x["key"]))

    def test_unmodified_copy_builder(self):
        orig = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertIs(orig, orig.modified_copy_builder().build())

    def test_modified_copy_builder(self):
        orig = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        updated = orig.modified_copy_builder().put(4, 5).build()
        expected = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6, 5]})
        self.assertEqual(expected, updated)

    def test_filter_keys(self):
        orig = ImmutableListMultiDict.of({1: [1], 2: [2], 3: [3], 4: [4]})
        evens = orig.filter_keys(lambda x: x % 2 == 0)
        self.assertEqual(ImmutableListMultiDict.of({2: [2], 4: [4]}), evens)
        all = orig.filter_keys(lambda x: x)
        self.assertEqual(orig, all)

    def test_len(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        # note 5, not 4, because the list version maintains distinctness
        self.assertEqual(5, len(x))
        # len's implementation often does caching, so test it works twice
        self.assertEqual(5, len(x))

    def test_inversion(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3, 6], 4: [5, 6]})
        reference_set_based = ImmutableSetMultiDict.of(
            {2: [1], 3: [1], 5: [4], 6: [1, 4]}
        )
        # 2->1 appears twice because 1->2 appears twice in the source
        reference_list_based = ImmutableListMultiDict.of(
            {2: [1, 1], 3: [1], 5: [4], 6: [1, 4]}
        )
        self.assertEqual(reference_set_based, x.invert_to_set_multidict())
        self.assertEqual(reference_list_based, x.invert_to_list_multidict())

    def test_pickling(self):
        self.assertEqual(
            pickle.loads(
                pickle.dumps(immutablelistmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]))
            ),
            immutablelistmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]),
        )
        self.assertEqual(
            pickle.loads(pickle.dumps(immutablelistmultidict())), immutablelistmultidict()
        )
        self.assertEqual(
            immutablelistmultidict([(1, (2, 2, 3, 6)), (4, (5, 6))]).__reduce__(),
            (immutablelistmultidict, (((1, (2, 2, 3, 6)), (4, (5, 6))),)),
        )
        self.assertEqual(
            immutablelistmultidict().__reduce__(), (immutablelistmultidict, ((),))
        )

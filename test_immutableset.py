from collections.abc import Set
from unittest import TestCase

from flexnlp.utils.immutablecollections import ImmutableSet, ImmutableList


class TestImmutableSet(TestCase):
    def test_empty_set(self):
        empty = ImmutableSet.empty()
        self.assertEqual(set(empty), set())

    def test_basic(self):
        source = {1, 2, 3}
        set1 = ImmutableSet.of(source)
        self.assertEqual(set(set1), source)
        self.assertEqual(len(set1), 3)
        self.assertTrue(1 in set1)
        self.assertFalse(4 in set1)

    def test_return_identical_immutable(self):
        set1 = ImmutableSet.of([1, 2, 3])
        set2 = ImmutableSet.of(set1)
        self.assertIs(set1, set2)

    def test_singleton_empty(self):
        empty = ImmutableSet.empty()
        empty2 = ImmutableSet.empty()
        self.assertIs(empty, empty2)

    def test_hash_eq(self):
        set1 = ImmutableSet.of({1, 2, 3})
        set2 = ImmutableSet.of({1, 2, 3})
        set3 = ImmutableSet.of({1, 2})

        self.assertEqual(set1, set2)
        self.assertNotEqual(set1, set3)

        val = object()
        d = {set1: val}
        self.assertEqual(d[set2], val)
        self.assertEqual(hash(set2), hash(set1))
        self.assertTrue(set3 not in d)

    def test_immutable(self):
        source = {1, 2, 3}
        set1 = ImmutableSet.of(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            set1.add(4)
        # Update doesn't affect original
        source.add(4)
        self.assertNotEqual(ImmutableSet.of(source), set1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableSet([1, 2, 3])

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            ImmutableSet.of(7)

    def test_init(self):
        source = [1, 2, 3]
        # Able to use a non-set iterable
        set1 = ImmutableSet.of(source)
        set2 = ImmutableSet.of(set(source))
        self.assertEqual(set1, set2)

    def test_unhashable(self):
        source = [[1, 2, 3]]
        # Cannot create using unhashable values
        with self.assertRaises(TypeError):
            ImmutableSet.of(source)

    def test_isinstance(self):
        set1 = ImmutableSet.of([1, 2, 3])
        # Note that this is collections.abc.Set, not typing.Set,
        # which is mutable
        self.assertTrue(isinstance(set1, Set))

    def test_slots(self):
        self.assertFalse(hasattr(ImmutableSet.of([1, 2, 3]), '__dict__'))

    def test_repr(self):
        self.assertEqual("i{1, 2, 3}", repr(ImmutableSet.of([1, 2, 3, 2])))

    def test_str(self):
        self.assertEqual("{1, 2, 3}", str(ImmutableSet.of([1, 2, 3, 2])))

    def test_type_testing(self):
        ImmutableSet.of([1, 2, 3], check_top_type_matches=int)
        with self.assertRaises(TypeError):
            ImmutableSet.of([1, 2, "three"], check_top_type_matches=int)
        string_set = ImmutableSet.of(["one", "two", "three"], check_top_type_matches=str)
        # this is fine
        ImmutableSet.of(string_set, check_top_type_matches=str)
        with self.assertRaises(TypeError):
            ImmutableSet.of(string_set, check_top_type_matches=int)

        # we want to check that type checking still works when the original immutable set wasn't
        # typed checked up front
        unchecked_string_set = ImmutableSet.of(["one", "two", "three"])
        ImmutableSet.of(unchecked_string_set, check_top_type_matches=str)
        with self.assertRaises(TypeError):
            ImmutableSet.of(unchecked_string_set, check_top_type_matches=int)

    def test_as_list(self):
        self.assertEqual(ImmutableList.of([3, 1, 2]), ImmutableSet.of([3, 1, 2]).as_list())

    def test_require_ordered_input(self):
        with self.assertRaises(ValueError):
            ImmutableSet.of({"a", "b", "c"}, require_ordered_input=True)
            ImmutableSet.builder(require_ordered_input=True).add_all({"a", "b", "c"})

    def test_order_irrelevant_for_equals_hash(self):
        x = ImmutableSet.of(["known", "jump"])
        y = ImmutableSet.of(["jump", "known"])
        self.assertEqual(x, y)
        self.assertEqual(hash(x), hash(y))

    def test_ordering(self):
        self.assertEqual(ImmutableList.of(["a", "b", "c"]),
                         ImmutableSet.builder(order_key=lambda x: x)
                         .add_all(["b", "c", "a"]).build().as_list())

    def test_difference(self):
        self.assertEqual(ImmutableSet.of(["a", "c"]),
                         ImmutableSet.of(["a", "b", "c"]).difference(ImmutableSet.of(["b", "d"])))
        self.assertEqual(ImmutableSet.of(["a", "c"]),
                         ImmutableSet.of(["a", "b", "c"]) - ImmutableSet.of(["b", "d"]))

    def test_union(self):
        self.assertEqual(ImmutableSet.of(["a", "c", "b"]),
                         ImmutableSet.of(["a", "c"]).union(ImmutableSet.of(["b", "c"])) )

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source = {1, 2, 3}
        dict1 = ImmutableSet.of(source)
        return next(iter(dict1))

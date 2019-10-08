import pickle
from collections.abc import Set
from unittest import TestCase
from unittest.mock import patch

from immutablecollections import (
    ImmutableSet,
    immutableset,
    immutableset_from_unique_elements,
)


class TestImmutableSet(TestCase):
    def test_empty(self):
        empty = immutableset()
        self.assertEqual(0, len(empty))
        empty2 = immutableset([])
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)

    def test_empty_singleton(self):
        empty1 = immutableset()
        empty2 = immutableset()
        self.assertIs(empty1, empty2)
        empty3 = immutableset([])
        self.assertIs(empty1, empty3)

    def test_basic(self):
        source = (1, 2, 3)
        set1 = immutableset(source)
        self.assertEqual(set(set1), set(source))
        self.assertEqual(len(set1), 3)
        self.assertTrue(1 in set1)
        self.assertFalse(4 in set1)

    def test_return_identical_immutable(self):
        set1 = immutableset([1, 2, 3])
        set2 = immutableset(set1)
        self.assertIs(set1, set2)

    def test_hash_eq(self):
        set1 = immutableset((1, 2, 3))
        set2 = immutableset((1, 2, 3))
        set3 = immutableset((1, 2))
        set4 = immutableset((3, 1, 2))

        self.assertEqual(set1, set2)
        self.assertNotEqual(set1, set3)
        self.assertEqual(set1, set4)

        val = object()
        d = {set1: val}
        self.assertEqual(d[set2], val)
        self.assertEqual(hash(set2), hash(set1))
        self.assertTrue(set3 not in d)

        # hash does not rely on order
        self.assertEqual(hash(set1), hash(set4))

        # equality with built-in types
        self.assertEqual({1, 2, 3}, set4)
        self.assertEqual(set4, {1, 2, 3})
        singleton_set = immutableset([2])
        self.assertEqual({2}, singleton_set)
        self.assertEqual(singleton_set, {2})
        self.assertEqual(set(), immutableset())
        self.assertEqual(immutableset(), set())

        self.assertEqual(frozenset([1, 2, 3]), set4)
        self.assertEqual(set4, frozenset([1, 2, 3]))

        # hash matches frozenset hash
        self.assertEqual(hash(frozenset([1, 2, 3])), hash(set4))
        self.assertEqual(hash(frozenset([2])), hash(singleton_set))
        self.assertEqual(hash(frozenset()), hash(immutableset()))

    def test_immutable(self):
        source = [1, 2, 3]
        set1 = immutableset(source)
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            set1.add(4)
        # Update doesn't affect original
        source.append(4)
        self.assertNotEqual(immutableset(source), set1)

    def test_cannot_init(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            ImmutableSet([1, 2, 3])

    def test_bad_args(self):
        with self.assertRaises(TypeError):
            immutableset(7)

    def test_unhashable(self):
        source = [[1, 2, 3]]
        # Cannot create using unhashable values
        with self.assertRaises(TypeError):
            immutableset(source)

    def test_isinstance(self):
        set1 = immutableset([1, 2, 3])
        # Note that this is collections.abc.Set, not typing.Set,
        # which is mutable
        self.assertTrue(isinstance(set1, Set))

    def test_slots(self):
        self.assertFalse(hasattr(immutableset(), "__dict__"))
        self.assertFalse(hasattr(immutableset([1]), "__dict__"))
        self.assertFalse(hasattr(immutableset([1, 2, 3]), "__dict__"))

    def test_repr(self):
        self.assertEqual("i{1, 2, 3}", repr(immutableset([1, 2, 3, 2])))

    def test_str(self):
        self.assertEqual("{1, 2, 3}", str(immutableset([1, 2, 3, 2])))

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

    def test_require_ordered_input(self):
        with self.assertRaises(ValueError):
            immutableset({"a", "b", "c"})

    def test_order_irrelevant_for_equals_hash(self):
        x = immutableset(["known", "jump"])
        y = immutableset(["jump", "known"])
        self.assertEqual(x, y)
        self.assertEqual(hash(x), hash(y))

    def test_ordering(self):
        self.assertEqual(
            ("a", "b", "c"), tuple(immutableset(["b", "c", "a"], order_key=lambda x: x))
        )

    # pylint: disable=blacklisted-name
    def test_comparisons(self):
        foo = {1, 2}
        bar = immutableset([1, 2, 3])
        meep = {1, 2, 3, 4}

        self.assertTrue(foo < bar)
        self.assertTrue(bar < meep)
        self.assertFalse(bar < bar)
        self.assertTrue(foo <= bar)
        self.assertTrue(foo <= immutableset(tuple(foo)))
        self.assertTrue(bar <= meep)
        self.assertTrue(bar <= bar)
        self.assertTrue(bar <= immutableset(bar))

        self.assertTrue(bar > foo)
        self.assertTrue(meep > bar)
        self.assertFalse(bar > bar)
        self.assertTrue(bar >= foo)
        self.assertTrue(immutableset(tuple(foo)) >= foo)
        self.assertTrue(meep >= bar)
        self.assertTrue(bar >= bar)
        self.assertTrue(immutableset(bar) >= bar)

    def test_issubset(self):
        empty = immutableset()
        s1 = immutableset([1, 2, 3, 3, 2, 1])
        s2 = immutableset([1, 2, 3, 4])
        self.assertTrue(s1.issubset(s2))
        self.assertFalse(s2.issubset(s1))
        self.assertTrue(empty.issubset(s1))
        # issubset is <=, not <
        self.assertTrue(empty.issubset(empty))
        self.assertFalse(s1.issubset(empty))

    def test_issuperset(self):
        empty = immutableset()
        s1 = immutableset([1, 2, 3, 3, 2, 1])
        s2 = immutableset([1, 2, 3, 4])
        self.assertFalse(s1.issuperset(s2))
        self.assertTrue(s2.issuperset(s1))
        self.assertFalse(empty.issuperset(s1))
        # issuperset is >=, not >
        self.assertTrue(empty.issuperset(empty))
        self.assertTrue(s1.issuperset(empty))

    def test_union(self):
        s1 = immutableset(["a", "c", "b"])
        s2 = immutableset(["a", "c"])
        s3 = immutableset(["b", "c"])
        self.assertEqual(s1, s2.union(s3))
        self.assertEqual(s1, s2 | s3)

    def test_difference(self):
        self.assertEqual(
            immutableset(["a", "c"]),
            immutableset(["a", "b", "c"]).difference(immutableset(["b", "d"])),
        )
        self.assertEqual(
            immutableset(["a", "c"]),
            immutableset(["a", "b", "c"]) - immutableset(["b", "d"]),
        )

    def test_symmetric_difference(self):
        s1 = immutableset([1, 2, 3, 8])
        s2 = immutableset([1, 2, 3, 4, 5, 6, 7])
        s3 = immutableset([4, 5, 6, 7, 8])
        self.assertEqual(s1, s2 ^ s3)
        self.assertEqual(s1, s3 ^ s2)
        self.assertEqual(s1, s2.symmetric_difference(s3))
        self.assertEqual(s1, s3.symmetric_difference(s2))

    def test_copy(self):
        s1 = immutableset([1, 2, 3, 8])
        s1c = s1.copy()
        self.assertEqual(s1, s1c)
        self.assertEqual(hash(s1), hash(s1c))

    def test_count(self):
        s = immutableset([1, 2, 3, 3, 2, 1])
        self.assertEqual(1, s.count(2))
        self.assertEqual(0, s.count(4))

    def test_reversed(self):
        s = immutableset(["b", "a", "c", "b"])
        self.assertEqual(["c", "a", "b"], list(reversed(s)))

    def test_index(self):
        s = immutableset(["a", "c", "b", "c"])
        self.assertEqual(1, s.index("c"))
        with self.assertRaises(ValueError):
            s.index("z")

    # pylint: disable=pointless-statement
    def test_singleton_index(self):
        s = ImmutableSet.of([1])

        self.assertEqual(1, s[0])
        self.assertEqual(1, s[-1])
        with self.assertRaises(IndexError):
            s[2]
        with self.assertRaises(IndexError):
            s[-2]
        with self.assertRaises(IndexError):
            s[25]
        with self.assertRaises(IndexError):
            s[-25]

    def test_singleton_slice(self):
        s = immutableset([1])

        self.assertEqual(s, s[0:1])
        self.assertEqual(s, s[-1:1])
        self.assertEqual(s, s[0:])
        self.assertEqual(s, s[:1])
        self.assertEqual(s, s[:50])
        self.assertEqual(s, s[-2:])

        self.assertEqual(immutableset(), s[1:5])
        self.assertEqual(immutableset(), s[51:56])
        self.assertEqual(immutableset(), s[-5:-1])
        self.assertEqual(immutableset(), s[-1:0])
        self.assertEqual(immutableset(), s[1:])

        self.assertEqual(immutableset(), s[5:1])

        self.assertEqual(s, s[0:1:1])
        self.assertEqual(s, s[1:-50:-1])
        self.assertEqual(s, s[0:1:5])
        self.assertEqual(s, s[1:-1:-60])

        with self.assertRaises(ValueError):
            s[0:1:0]

    def test_slice(self):
        self.assertEqual(2, immutableset([1, 2, 3])[1])
        self.assertEqual((2, 3), immutableset([1, 2, 3])[1:])

    @staticmethod
    def type_annotations() -> int:
        # Just to check for mypy warnings
        source = (1, 2, 3)
        dict1 = immutableset(source)
        return next(iter(dict1))

    # A reminder that when patching, it must be done where used, not where it is defined.
    @patch("immutablecollections._immutableset.DICT_ITERATION_IS_DETERMINISTIC", False)
    def test_dict_iteration_is_not_deterministic(self):
        source = {"b": 2, "c": 3, "a": 1}
        value_error_regex = r"Attempting to initialize an ImmutableSet from a dict view\."
        with self.assertRaisesRegex(ValueError, value_error_regex):
            immutableset(source.keys())
        with self.assertRaisesRegex(ValueError, value_error_regex):
            immutableset(source.values())
        with self.assertRaisesRegex(ValueError, value_error_regex):
            immutableset(source.items())

        with self.assertRaisesRegex(
            ValueError,
            r"Attempting to initialize an ImmutableSet from a non-ImmutableSet set\.",
        ):
            immutableset({"b", "c", "a"})

    @patch("immutablecollections._immutableset.DICT_ITERATION_IS_DETERMINISTIC", True)
    def test_dict_iteration_is_deterministic(self):
        source = {"b": 2, "c": 3, "a": 1}
        immutableset(source.keys())
        immutableset(source.values())
        immutableset(source.items())

        with self.assertRaisesRegex(
            ValueError,
            r"Attempting to initialize an ImmutableSet from a non-ImmutableSet set\.",
        ):
            immutableset({"b", "c", "a"})

    def test_pickling(self):
        self.assertEqual(pickle.loads(pickle.dumps(immutableset([5]))), immutableset([5]))
        self.assertEqual(
            pickle.loads(pickle.dumps(immutableset([5, 2]))), immutableset([5, 2])
        )
        self.assertEqual(pickle.loads(pickle.dumps(immutableset())), immutableset())
        self.assertEqual(immutableset([5, 2]).__reduce__(), (immutableset, ((5, 2),)))
        self.assertEqual(immutableset([5]).__reduce__(), (immutableset, ((5,),)))
        self.assertEqual(immutableset().__reduce__(), (immutableset, ((),)))

    def test_subtract_from_other_set_types(self):
        # normal sets on LHS
        self.assertEqual({5, 6}, {4, 5, 6} - immutableset([2, 3, 4]))
        self.assertEqual(set(), set() - immutableset([]))
        self.assertEqual({2, 3}, {2, 3} - immutableset([]))
        self.assertEqual(set(), {2, 3} - immutableset([2, 3]))

        # frozensets on LHS
        self.assertEqual({5, 6}, frozenset([4, 5, 6]) - immutableset([2, 3, 4]))
        self.assertEqual({"a"}, frozenset(["a", "b"]) - immutableset(["b", "c"]))

    def test_forbid_duplicate_elements(self):
        bad = [4, 6, 7, 9, 7]
        with self.assertRaises(ValueError):
            immutableset(bad, forbid_duplicate_elements=True)
        with self.assertRaises(ValueError):
            immutableset_from_unique_elements(bad)
        with self.assertRaises(ValueError):
            immutableset((x for x in bad), forbid_duplicate_elements=True)
        with self.assertRaises(ValueError):
            immutableset_from_unique_elements(x for x in bad)

        good = [3, 7, 5, 9]
        immutableset(good, forbid_duplicate_elements=True)
        immutableset_from_unique_elements(good)
        immutableset((x for x in good), forbid_duplicate_elements=True)
        immutableset_from_unique_elements(x for x in good)

from unittest import TestCase, skip

from flexnlp.utils.immutablecollections.immutablemultidict import ImmutableSetMultiDict, \
    ImmutableListMultiDict


class TestImmutableMultiDict(TestCase):
    def test_set_repr(self):
        self.assertEqual("i{1: {2, 3}, 4: {5, 6}}",
                         repr(ImmutableSetMultiDict.of(
                             {1: [2, 3], 4: [5, 6]})))

    def test_set_str(self):
        self.assertEqual("{1: {2, 3}, 4: {5, 6}}",
                         str(ImmutableSetMultiDict.of(
                             {1: [2, 3], 4: [5, 6]})))

    def test_unmodified_copy_builder(self):
        ref: ImmutableSetMultiDict[str, int] = (ImmutableSetMultiDict.builder()
                                                .put('foo', 5).put('bar', 6)
                                                .put('foo', 4).build())

        self.assertEqual(ref, ref.modified_copy_builder().build())

    def test_modified_copy_builder(self):
        start: ImmutableSetMultiDict[str, int] = (ImmutableSetMultiDict.builder()
                                                  .put('foo', 5).put('bar', 6)
                                                  .put('foo', 4).build())
        updated = start.modified_copy_builder().put('bar', 1).put('foo', 7).put('meep', -1).build()

        ref: ImmutableSetMultiDict[str, int] = (ImmutableSetMultiDict.builder()
                                                .put('foo', 5).put('bar', 6)
                                                .put('foo', 4).put('foo', 7)
                                                .put('bar', 1).put('meep', -1).build())
        self.assertEqual(ref, updated)


class TestImmutableListMultiDict(TestCase):
    def test_empty(self):
        empty = ImmutableListMultiDict.empty()
        self.assertEqual(0, len(empty))
        empty2 = ImmutableListMultiDict.of(dict())
        self.assertEqual(0, len(empty2))
        self.assertEqual(empty, empty2)
        empty3 = ImmutableListMultiDict.builder().build()
        self.assertEqual(0, len(empty3))
        self.assertEqual(empty, empty3)

    @skip
    def test_empty_singleton(self):
        empty = ImmutableListMultiDict.empty()
        empty2 = ImmutableListMultiDict.of(dict())
        self.assertEqual(id(empty), id(empty2))
        empty3 = ImmutableListMultiDict.builder().build()
        self.assertEqual(id(empty), id(empty3))

    def test_of(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        self.assertEqual([2, 2, 3], list(x[1]))

    def test_repr(self):
        self.assertEqual("i{1: [2, 2, 3]}", repr(ImmutableListMultiDict.of({1: [2, 2, 3]})))

    def test_str(self):
        self.assertEqual("{1: [2, 2, 3]}", str(ImmutableListMultiDict.of({1: [2, 2, 3]})))

    def test_immutable_keys(self):
        x = ImmutableListMultiDict.of({1: [2, 2, 3], 4: [5, 6]})
        # TypeError: 'FrozenDictBackedImmutableListMultiDict' object does not support item
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

    def test_builder(self):
        b: ImmutableListMultiDict.Builder[str, int] = ImmutableListMultiDict.builder()
        b.put('foo', [1, 2, 3])

    def test_type_checking(self):
        b: ImmutableListMultiDict.Builder[str, int] = ImmutableListMultiDict.builder()
        b.put('foo', [1, 2, 3])
        b.put(1, 2)
        b.put(1, [2, 3])
        b.put(1, "two")
        print(b.build())
        # {'foo': [[1, 2, 3]], 1: [2, [2, 3], 'two']} -- oops

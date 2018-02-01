from unittest import TestCase

from flexnlp.utils.immutablecollections.immutablemultidict import ImmutableSetMultiDict


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

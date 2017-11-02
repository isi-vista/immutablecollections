from unittest import TestCase

from flexnlp.util.immutablecollections import ImmutableMixin, FrozenInstanceError


class Immutable(ImmutableMixin):

    def __init__(self, val):
        object.__setattr__(self, 'val', val)


class TestImmutableMixin(TestCase):

    def test_mixin(self):
        x = Immutable(7)
        self.assertEqual(x.val, 7)
        with self.assertRaises(FrozenInstanceError):
            x.val = 8
        with self.assertRaises(FrozenInstanceError):
            del x.val

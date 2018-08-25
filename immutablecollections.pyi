import typing

_T = typing.TypeVar('_T')
_T2 = typing.TypeVar('_T2')

_AnySet = typing.Union['ImmutableSet[_T2]', typing.AbstractSet[_T2]]


class ImmutableSet(typing.Generic[_T]):
    def union(self, iterable: typing.Iterable[_T2]) -> 'ImmutableSet[_T2]': ...

    def intersection(self, other_set: _AnySet[_T2]) -> 'ImmutableSet[_T2]': ...

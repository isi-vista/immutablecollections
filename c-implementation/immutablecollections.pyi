import typing

_T = typing.TypeVar('_T')
_T2 = typing.TypeVar('_T2')

_AnySet = typing.Union['ImmutableSet[_T2]', typing.AbstractSet[_T2]]


class ImmutableSet(typing.Generic[_T], typing.Sized):
    @staticmethod
    def empty() -> 'ImmutableSet[typing.Any]': ...

    @staticmethod
    def of(iterable: typing.Iterable[_T2]) -> 'ImmutableSet[_T2]': ...

    # TODO: how to type-stub default argument here
    @staticmethod
    def builder() -> 'ImmutableSet.Builder': ...


    def union(self, iterable: typing.Iterable[_T2]) -> 'ImmutableSet[_T2]': ...

    def intersection(self, other_set: _AnySet[_T2]) -> 'ImmutableSet[_T2]': ...

    def difference(self, other_set: _AnySet[_T2]) -> 'ImmutableSet[_T2]': ...

    class Builder(typing.Generic[_T2]):
        def add(self, item: _T2) -> 'ImmutableSet.Builder[_T2]': ...

        def add_all(self, item: typing.Iterable[_T2]) -> 'ImmutableSet.Builder[_T2]': ...

        def build(self) -> ImmutableSet[_T2]: ...

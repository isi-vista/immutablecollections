from abc import ABCMeta
from typing import (
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Sized,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from attr import attrib, attrs

from immutablecollections.immutablecollection import ImmutableCollection

T = TypeVar("T")  # pylint:disable=invalid-name
T2 = TypeVar("T2")


def immutablelist(iterable: Optional[Iterable[T]] = None) -> "ImmutableList[T]":
    """
    Create an immutable list with the given contents.

    The iteration order of the created list will match *iterable*.  If *iterable* is `None`, an
    empty `ImmutableList` will be returned.

    If *iterable* is already an ``ImmutableList``, *iterable* itself will be returned.
    """
    # immutablelist() should return an empty set
    if iterable is None:
        return _EMPTY_IMMUTABLE_LIST

    if isinstance(iterable, ImmutableList):
        # if an ImmutableList is input, we can safely just return it,
        # since the object can safely be shared
        return iterable

    values_as_tuple = tuple(iterable)

    if values_as_tuple:
        return _TupleBackedImmutableList(iterable)
    else:
        return _EMPTY_IMMUTABLE_LIST


class ImmutableList(
    Generic[T], ImmutableCollection[T], Sequence[T], Iterable[T], metaclass=ABCMeta
):
    __slots__ = ()

    # Signature of the of method varies by collection
    # pylint: disable = arguments-differ
    @staticmethod
    def of(seq: Iterable[T]) -> "ImmutableList[T]":
        """
        Use of this method is deprecated. Prefer the module-level ``immutablelist``.
        """
        if isinstance(seq, ImmutableList):
            return seq
        else:
            return ImmutableList.builder().add_all(seq).build()  # type: ignore

    @staticmethod
    def empty() -> "ImmutableList[T]":
        return _EMPTY_IMMUTABLE_LIST

    @staticmethod
    def builder() -> "ImmutableList.Builder[T]":
        return ImmutableList.Builder()

    class Builder(Generic[T2], Sized):
        """
        Use of this builder is deprecated. Prefer to pass a regular ``list`` to ``immutablelist``
        """

        def __init__(self):
            self._list: List[T2] = []

        def add(self, item: T2) -> "ImmutableList.Builder[T2]":
            self._list.append(item)
            return self

        def add_all(self, items: Iterable[T2]) -> "ImmutableList.Builder[T2]":
            self._list.extend(items)
            return self

        def __len__(self) -> int:
            return len(self._list)

        def build(self) -> "ImmutableList[T2]":
            if self._list:
                return _TupleBackedImmutableList(self._list)
            else:
                return _EMPTY_IMMUTABLE_LIST

    def __repr__(self):
        return "i" + str(self)

    def __str__(self):
        return "%s" % list(self)


@attrs(frozen=True, slots=True, repr=False)
class _TupleBackedImmutableList(ImmutableList[T]):

    _list: Tuple[T, ...] = attrib(converter=tuple)

    @overload
    def __getitem__(self, index: int) -> T:  # pylint:disable=function-redefined
        pass  # pragma: no cover

    @overload
    def __getitem__(  # pylint:disable=function-redefined
        self, index: slice
    ) -> Sequence[T]:
        pass  # pragma: no cover

    def __getitem__(  # pylint:disable=function-redefined
        self, index: Union[int, slice]
    ) -> Union[T, Sequence[T]]:
        # this works because Tuple can handle either type of index
        return self._list[index]

    def __iter__(self) -> Iterator[T]:
        return self._list.__iter__()

    def __len__(self):
        return self._list.__len__()


# Singleton instance for empty
_EMPTY_IMMUTABLE_LIST: ImmutableList = _TupleBackedImmutableList(())

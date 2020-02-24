from abc import ABCMeta, abstractmethod
from itertools import chain, islice
from typing import (
    AbstractSet,
    Any,
    Callable,
    Container,
    FrozenSet,
    Generic,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    MutableSet,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    ValuesView,
    overload,
)

from immutablecollections import immutablecollection
from immutablecollections._utils import DICT_ITERATION_IS_DETERMINISTIC

T = TypeVar("T")
# necessary because inner classes cannot share typevars
T2 = TypeVar("T2")  # pylint:disable=invalid-name
V = TypeVar("V")
SelfType = TypeVar("SelfType")  # pylint:disable=invalid-name
ViewTypes = (KeysView, ValuesView, ItemsView)  # pylint:disable=invalid-name


def immutableset(
    iterable: Optional[Iterable[T]] = None,
    *,
    disable_order_check: bool = False,
    forbid_duplicate_elements: bool = False,
) -> "ImmutableSet[T]":
    """
    Create an immutable set with the given contents.

    The iteration order of the created set will match *iterable*.  Note that for this reason,
    when initializing an ``ImmutableSet`` from a constant collection expression, prefer a
    list over a set.  We attempt to catch a handful of common cases in which deterministic
    iteration order would be discarded: initializing from a (non-``ImmutableSet``) set or
    (on CPython < 3.6.0 and other Pythons < 3.7.0) initializing from a dictionary view. In
    these cases we will throw an exception as a warning to the programmer, but this behavior
    could be removed in the future and should not be relied upon.  This check may be disabled
    by setting *disable_order_check* to ``True``.

    If *forbid_duplicate_elements* is ``True`` and one item occurs twice in *iterable*, then
    a ``ValueError`` will be thrown.

    If *iterable* is already an ``ImmutableSet``, *iterable* itself will be returned.
    """
    # immutableset() should return an empty set
    if iterable is None:
        return _EMPTY

    if isinstance(iterable, ImmutableSet):
        # if an ImmutableSet is input, we can safely just return it,
        # since the object can safely be shared
        return iterable

    if not disable_order_check:
        if not DICT_ITERATION_IS_DETERMINISTIC:
            # See https://github.com/isi-vista/immutablecollections/pull/36
            # for benchmarks as to why the split conditional is faster even
            # with short-circuiting.
            if isinstance(iterable, ViewTypes):
                raise ValueError(
                    "Attempting to initialize an ImmutableSet from "
                    "a dict view. On this Python version, this probably loses "
                    "determinism in iteration order.  If you don't care "
                    "or are otherwise sure your input has deterministic "
                    "iteration order, specify disable_order_check=True"
                )
        if isinstance(iterable, AbstractSet) and not isinstance(iterable, ViewTypes):
            # dict order is deterministic in this interpreter, so order
            # of KeysView and ItemsView from standard dicts will be as well.
            # These could be user implementations of this interface which are
            # non-deterministic, but this check is just a courtesy to catch the
            # most common cases anyway.
            raise ValueError(
                "Attempting to initialize an ImmutableSet from "
                "a non-ImmutableSet set. This probably loses "
                "determinism in iteration order.  If you don't care "
                "or are otherwise sure your input has deterministic "
                "iteration order, specify disable_order_check=True"
            )

    if forbid_duplicate_elements:
        # We check for duplicate elements by comparing the original iterable length with the output
        # set length. Some iterables don't provide a __len__ or are consumed by iteration, so we
        # listify the iterable to be safe.
        iterable = list(iterable)
        original_length = len(iterable)  # must be recorded here for mypy to be happy

    iteration_order = []
    containment_set: MutableSet[T] = set()
    for value in iterable:
        if value not in containment_set:
            containment_set.add(value)
            iteration_order.append(value)

    if forbid_duplicate_elements and len(containment_set) != original_length:
        seen_once: Set[T] = set()
        seen_twice: Set[T] = set()
        for item in iterable:
            if item not in seen_once:
                seen_once.add(item)
            else:
                seen_twice.add(item)
        # seen_twice is guaranteed to be nonempty
        raise ValueError(
            "forbid_duplicate_elements=True, but some elements "
            f"occur multiple times in input: {seen_twice}"
        )

    if iteration_order:
        if len(iteration_order) == 1:
            return _SingletonImmutableSet(iteration_order[0], None)
        else:
            return _FrozenSetBackedImmutableSet(containment_set, iteration_order, None)
    else:
        return _EMPTY


def immutableset_from_unique_elements(
    iterable: Optional[Iterable[T]] = None, *, disable_order_check: bool = False
):
    """
    Create an immutableset from *iterable*. If one item occurs twice in *iterable*, then
    a ``ValueError`` will be thrown. More information in ``immutablecollections.immutableset``.
    """
    return immutableset(
        iterable, disable_order_check=disable_order_check, forbid_duplicate_elements=True
    )


# typing.AbstractSet matches collections.abc.Set
class ImmutableSet(  # pylint: disable=duplicate-bases
    Generic[T],
    immutablecollection.ImmutableCollection[T],
    AbstractSet[T],
    Sequence[T],
    metaclass=ABCMeta,
):
    __slots__ = ()
    """
    A immutable set with deterministic iteration order.

    The set will be unmodifiable by normal means.

    The iteration order of the set will be the order in which elements were added. Iteration
    order is ignored when determining equality and hash codes.

    Optional top-level run-time type setting is supported (see of()).

    ImmutableSets should be created via of() or builder(), not by directly instantiating one of
    the sub-classes.

    For runtime type checks that wish to include ImmutableSet as well
    as the types set and frozenset, use collections.abc.Set or
    typing.AbstractSet. An ImmutableSet is not an instance of
    typing.Set, as that matches the built-in mutable set type.
    """

    # note to implementers: if a new implementing class is created besides the frozen set one,
    # we need to change how the equals method works

    # Signature of the of method varies by collection
    # pylint: disable = arguments-differ
    @staticmethod
    def of(
        seq: Iterable[T],
        check_top_type_matches: Optional[Type[T]] = None,
        require_ordered_input: bool = False,
    ) -> "ImmutableSet[T]":
        """
        Deprecated - prefer ``immutableset`` module-level factory method.
        """
        # pylint:disable=protected-access
        if isinstance(seq, ImmutableSet):
            if check_top_type_matches:
                # we assume each sub-class provides _top_level_type
                if seq._top_level_type:  # type: ignore
                    _check_issubclass(
                        seq._top_level_type, check_top_type_matches  # type: ignore
                    )  # type: ignore
                else:
                    _check_all_isinstance(seq, check_top_type_matches)
            return seq
        else:
            return (
                ImmutableSet.builder(
                    check_top_type_matches=check_top_type_matches,
                    require_ordered_input=require_ordered_input,
                )
                .add_all(seq)
                .build()
            )

    @staticmethod
    def empty() -> "ImmutableSet[T]":
        """
        Get an empty ImmutableSet.
        """
        return _EMPTY

    def issubset(self, other: Iterable[T]) -> bool:
        """
        This set is a subset of another set if all the elements of this set are
        are contained in the other set.

        Note that this operation is equivalent to `self <= other`. For determining whether or not
         this set is a _proper_ subset of another set, use `self < other`.
        """
        if isinstance(other, AbstractSet):
            return self.__le__(other)
        return self.__le__(immutableset(other))

    def issuperset(self, other: Iterable[T]) -> bool:
        """
        This set is a superset of another set if all the elements of the other set
        are contained in this set.

        Note that this operation is equivalent to `self >= other`. For determining whether or not
        this set is a _proper_ superset of another set, use `self > other`.
        """
        if isinstance(other, AbstractSet):
            return self.__ge__(other)
        return self.__ge__(immutableset(other))

    # we would really like this to be AbstractSet[ExtendsT] but Python doesn't support it
    def union(
        self, other: Iterable[T], check_top_type_matches: Optional[Type[T]] = None
    ) -> "ImmutableSet[T]":
        """
        Get the union of this set and another.

        If check top level types is provided, all elements of both sets must match the specified
        type.
        """
        if check_top_type_matches:
            for (side_name, side) in (("left", self), ("right", other)):
                items_not_matching = [
                    x for x in side if not isinstance(x, check_top_type_matches)
                ]
                if items_not_matching:
                    raise TypeError(
                        f"Items in immutableset union were asked to match "
                        f"{check_top_type_matches}, but got "
                        f"{list(islice(items_not_matching, 10))} "
                        f"on the {side_name}"
                    )
            return (
                ImmutableSet.builder(check_top_type_matches)
                .add_all(self)
                .add_all(other)
                .build()
            )
        else:
            # When we don't need to do check_top_type_matches,
            # we can use the more efficient factory method.
            return immutableset(chain(self, other))

    # we deliberately tighten the type bounds from our parent
    def __or__(self, other: AbstractSet[T]) -> "ImmutableSet[T]":  # type: ignore
        """
        Get the union of this set and another without type checking.
        """
        return self.union(other)

    def intersection(self, other: Iterable[Any]) -> "ImmutableSet[T]":
        """
        Get the intersection of this set and another.

        If you know the set `x` is smaller then the set `y`, `x.intersection(y)` will be faster
        than `y.intersection(x)`.

        We don't provide an option to type-check here because any item in the resulting set
        should have already been in this set, so you can type check this set itself if you are
        concerned.
        """
        return (
            ImmutableSet.builder(
                check_top_type_matches=self._top_level_type  # type: ignore
            )
            .add_all(x for x in self if x in other)
            .build()
        )

    def __and__(self, other: AbstractSet[Any]) -> "ImmutableSet[T]":
        """
        Get the intersection of this set.
        """
        return self.intersection(other)

    def difference(self, other: AbstractSet[Any]) -> "ImmutableSet[T]":
        """
        Gets a new set with all items in this set not in the other.
        """
        return ImmutableSet.of(
            (x for x in self if x not in other),
            check_top_type_matches=self._top_level_type,  # type: ignore
        )

    def __sub__(self, other: AbstractSet[Any]) -> "ImmutableSet[T]":
        """
        Subtracts `other` from `self`. An item is included iff it is in `self` and not in `other`.
        """
        return self.difference(other)

    def __rsub__(self, other: AbstractSet[V]) -> "AbstractSet[V]":
        """
        Subtracts `self` from `other`. An item is included iff is in `other` and not in `self`.

        This method is necessary because it defines behavior for an `otherset - immutableset`.
        Without this method, otherset.__sub__(immutableset) would be called, which will typically
        fail.
        """
        return set(item for item in other if item not in self)

    def symmetric_difference(self, other: Iterable[V]) -> "AbstractSet[Union[T, V]]":
        """
        Return the union of elements that are in this set but not the other and elements that are
        in the other set but not this set (`(self - other) | (other - self)`).
        """
        if isinstance(other, AbstractSet):
            return self ^ other
        return self ^ immutableset(other)

    def copy(self) -> "ImmutableSet[T]":
        """
        Return this set.

        Because ImmutableSet is immutable, there is never a reason to copy it. This method is
        provided for compatibility with `set` and `frozenset`.
        """
        return self

    # we can be more efficient than Sequence's default implementation
    def count(self, value: Any) -> int:
        if value in self:
            return 1
        else:
            return 0

    def __repr__(self):
        return "i" + str(self)

    def __str__(self):
        # we use this rather than set() for when we add deterministic iteration order
        as_list = str(list(self))
        return "{%s}" % as_list[1:-1]

    @staticmethod
    def builder(
        check_top_type_matches: Optional[Type[T]] = None,
        require_ordered_input: bool = False,
        order_key: Callable[[T], Any] = None,
    ) -> "ImmutableSet.Builder[T]":
        """
        Gets an object which can build an ImmutableSet.

        If check_top_matches is specified, each element added to this set will be
        checked to be an instance of that type.

        If require_ordered_input is True (default False), an exception will be thrown if a
        non-sequence, non-ImmutableSet is used for add_all.  This is recommended to help
        encourage determinism.

        If order_key is present, the order of the resulting set will be sorted by
        that key function rather than in the usual insertion order.

        You can check item containment before building the set by using "in" on the builder.
        """
        # Optimization: We use two different implementations, one that checks types and one that
        # does not. Profiling revealed that this is faster than a single implementation that
        # conditionally checks types based on a member variable. Two separate classes are needed;
        # if you use a single class that conditionally defines add and add_all upon construction,
        # Python's method-lookup optimizations are defeated and you don't get any benefit.
        if check_top_type_matches is not None:
            return _TypeCheckingBuilder(
                top_level_type=check_top_type_matches,
                require_ordered_input=require_ordered_input,
                order_key=order_key,
            )
        else:
            return _NoTypeCheckingBuilder(
                require_ordered_input=require_ordered_input, order_key=order_key
            )

    class Builder(Generic[T2], Container[T2], metaclass=ABCMeta):
        @abstractmethod
        def add(self: SelfType, item: T2) -> SelfType:
            raise NotImplementedError()

        @abstractmethod
        def add_all(self: SelfType, items: Iterable[T2]) -> SelfType:
            raise NotImplementedError()

        @abstractmethod
        def __contains__(self, item):
            raise NotImplementedError()

        @abstractmethod
        def build(self) -> "ImmutableSet[T2]":
            raise NotImplementedError()


# When modifying this class, make sure any relevant changes are also made to _NoTypeCheckingBuilder
class _TypeCheckingBuilder(ImmutableSet.Builder[T]):
    def __init__(
        self,
        top_level_type: Optional[Type] = None,
        require_ordered_input: bool = False,
        order_key: Callable[[T], Any] = None,
    ) -> None:
        if not isinstance(top_level_type, (type, type(None))):
            raise TypeError(
                f"Expected instance of type {type:!r} or {type(None):!r} "
                f"but got type {type(top_level_type):!r} for top_level_type instead"
            )
        self._top_level_type = top_level_type
        if not isinstance(require_ordered_input, bool):
            raise TypeError(
                f"Expected instance of type {bool:!r} "
                "but got type {type(require_ordered_input):!r} for require_ordered_input instead"
            )
        self._require_ordered_input = require_ordered_input
        self._order_key = order_key

        self._set: AbstractSet[T] = set()
        self._iteration_order: List[T] = list()

    def add(self: SelfType, item: T) -> SelfType:
        # Any changes made to add should also be made to add_all
        if item not in self._set:
            # Optimization: Don't use use check_isinstance to cut down on method calls
            if not isinstance(item, self._top_level_type):
                raise TypeError(
                    "Expected instance of type {!r} but got type {!r} for {!r}".format(
                        self._top_level_type, type(item), item
                    )
                )
            self._set.add(item)
            self._iteration_order.append(item)
        return self

    def add_all(self: SelfType, items: Iterable[T]) -> SelfType:
        if (
            self._require_ordered_input
            and not (isinstance(items, Sequence) or isinstance(items, ImmutableSet))
            and not self._order_key
        ):
            raise ValueError(
                "Builder has require_ordered_input on, but provided collection "
                "is neither a sequence or another ImmutableSet.  A common cause "
                "of this is initializing an ImmutableSet from a set literal; "
                "prefer to initialize from a list instead to help preserve "
                "determinism."
            )

        # Optimization: These methods are looked up once outside the inner loop. Note that applying
        # the same approach to the containment check does not improve performance, probably because
        # the containment check syntax itself is already optimized.
        add = self._set.add
        append = self._iteration_order.append
        # Optimization: Store self._top_level_type to avoid repeated lookups
        top_level_type = self._top_level_type
        for item in items:
            # Optimization: to save method call overhead in an inner loop, we don't call add and
            # instead do the same thing. We don't use check_isinstance for the same reason.
            if item not in self._set:
                if not isinstance(item, top_level_type):
                    raise TypeError(
                        "Expected instance of type {!r} but got type {!r} for {!r}".format(
                            top_level_type, type(item), item
                        )
                    )
                add(item)
                append(item)

        return self

    def __contains__(self, item):
        return self._set.__contains__(item)

    def build(self) -> "ImmutableSet[T]":
        if self._set:
            if len(self._set) > 1:
                if self._order_key:
                    self._iteration_order.sort(key=self._order_key)
                return _FrozenSetBackedImmutableSet(
                    self._set, self._iteration_order, top_level_type=self._top_level_type
                )
            else:
                return _SingletonImmutableSet(
                    self._set.__iter__().__next__(), top_level_type=self._top_level_type
                )
        else:
            return _EMPTY


# When modifying this class, make sure any relevant changes are also made to _TypeCheckingBuilder
class _NoTypeCheckingBuilder(ImmutableSet.Builder[T]):
    def __init__(
        self, require_ordered_input: bool = False, order_key: Callable[[T], Any] = None
    ) -> None:
        if not isinstance(require_ordered_input, bool):
            raise TypeError(
                f"Expected instance of type {bool:!r} "
                "but got type {type(require_ordered_input):!r} for require_ordered_input instead"
            )
        self._require_ordered_input = require_ordered_input
        self._order_key = order_key

        self._set: AbstractSet[T] = set()
        self._iteration_order: List[T] = list()

    def add(self: SelfType, item: T) -> SelfType:
        # Any changes made to add should also be made to add_all
        if item not in self._set:
            self._set.add(item)
            self._iteration_order.append(item)
        return self

    def add_all(self: SelfType, items: Iterable[T]) -> SelfType:
        if (
            self._require_ordered_input
            and not (isinstance(items, Sequence) or isinstance(items, ImmutableSet))
            and not self._order_key
        ):
            raise ValueError(
                "Builder has require_ordered_input on, but provided collection "
                "is neither a sequence or another ImmutableSet.  A common cause "
                "of this is initializing an ImmutableSet from a set literal; "
                "prefer to initialize from a list instead to help preserve "
                "determinism."
            )

        # Optimization: These methods are looked up once outside the inner loop. Note that applying
        # the same approach to the containment check does not improve performance, probably because
        # the containment check syntax itself is already optimized.
        add = self._set.add
        append = self._iteration_order.append
        for item in items:
            # Optimization: to save method call overhead in an inner loop, we don't call add and
            # instead do the same thing.
            if item not in self._set:
                add(item)
                append(item)

        return self

    def __contains__(self, item):
        return self._set.__contains__(item)

    def build(self) -> "ImmutableSet[T]":
        if self._set:
            if len(self._set) > 1:
                if self._order_key:
                    self._iteration_order.sort(key=self._order_key)
                return _FrozenSetBackedImmutableSet(
                    self._set, self._iteration_order, top_level_type=None
                )
            else:
                return _SingletonImmutableSet(
                    self._set.__iter__().__next__(), top_level_type=None
                )
        else:
            return _EMPTY


class _FrozenSetBackedImmutableSet(ImmutableSet[T]):
    """
    Implementing class for the general case for ImmutableSet.

    This class should *never*
    be directly instantiated by users or the ImmutableSet contract may fail to be satisfied!
    """

    __slots__ = "_set", "_iteration_order", "_top_level_type"

    # pylint:disable=assigning-non-slot
    def __init__(
        self,
        init_set: Iterable[T],
        iteration_order: Sequence[T],
        top_level_type: Optional[Type],
    ) -> None:
        self._set: FrozenSet[T] = frozenset(init_set)
        self._iteration_order = tuple(iteration_order)
        self._top_level_type = top_level_type

    def __iter__(self) -> Iterator[T]:
        return self._iteration_order.__iter__()

    def __len__(self) -> int:
        return self._set.__len__()

    def __contains__(self, item) -> bool:
        return self._set.__contains__(item)

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
        return self._iteration_order[index]

    def __eq__(self, other):
        # pylint:disable=protected-access
        if isinstance(other, AbstractSet):
            return self._set == other
        else:
            return False

    def __hash__(self):
        return self._set.__hash__()

    def __reduce__(self):
        return (immutableset, (self._iteration_order,))


class _SingletonImmutableSet(ImmutableSet[T]):
    __slots__ = "_single_value", "_top_level_type"

    # pylint:disable=assigning-non-slot
    def __init__(self, single_value: T, top_level_type: Optional[Type]) -> None:
        self._single_value = single_value
        self._top_level_type = top_level_type

    def __iter__(self) -> Iterator[T]:
        return iter((self._single_value,))

    def __len__(self) -> int:
        return 1

    def __contains__(self, item) -> bool:
        return self._single_value == item

    @overload
    def __getitem__(self, index: int) -> T:  # pylint:disable=function-redefined
        pass  # pragma: no cover

    @overload
    def __getitem__(  # pylint:disable=function-redefined
        self, index: slice
    ) -> Sequence[T]:
        pass  # pragma: no cover

    def __getitem__(  # pylint:disable=function-redefined
        self, item: Union[int, slice]
    ) -> Union[T, Sequence[T]]:
        # this works because Tuple can handle either type of index
        if item == 0 or item == -1:
            return self._single_value
        elif isinstance(item, slice):
            if item.step is None or item.step > 0:
                if (
                    (item.start is None and item.stop is None)
                    or (item.start is None and (item.stop is None or item.stop >= 1))
                    or (item.start <= 0 and (item.stop is None or item.stop >= 1))
                ):
                    return self
                else:
                    return _EMPTY
            elif item.step < 0:
                return self.__getitem__(slice(item.stop, item.start, -item.step))
            else:
                raise ValueError("Can't slice with step size of zero.")
        else:
            raise IndexError(f"Index {item} out-of-bounds for size 1 ImmutableSet")

    def __eq__(self, other):
        # pylint:disable=protected-access
        if isinstance(other, AbstractSet):
            return len(other) == 1 and self._single_value in other
        else:
            return False

    def __hash__(self):
        return hash(frozenset((self._single_value,)))

    def __reduce__(self):
        return (immutableset, ((self._single_value,),))


# Singleton instance for empty
_EMPTY: ImmutableSet = _FrozenSetBackedImmutableSet((), (), None)

# copied from VistaUtils' precondtions.py to avoid a dependency loop
_ClassInfo = Union[type, Tuple[Union[type, Tuple], ...]]  # pylint:disable=invalid-name


def _check_issubclass(item, classinfo: _ClassInfo):
    if not issubclass(item, classinfo):
        raise TypeError(
            "Expected subclass of type {!r} but got {!r}".format(classinfo, type(item))
        )
    return item


def _check_all_isinstance(items: Iterable[Any], classinfo: _ClassInfo):
    for item in items:
        _check_isinstance(item, classinfo)


def _check_isinstance(item: T, classinfo: _ClassInfo) -> T:
    if not isinstance(item, classinfo):
        raise TypeError(
            "Expected instance of type {!r} but got type {!r} for {!r}".format(
                classinfo, type(item), item
            )
        )
    return item

from abc import ABCMeta
from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from immutablecollections._utils import DICT_ITERATION_IS_DETERMINISTIC
from immutablecollections.immutablecollection import ImmutableCollection

KT = TypeVar("KT")
VT = TypeVar("VT")
IT = Tuple[KT, VT]

# cannot share type variables between outer and inner classes
KT2 = TypeVar("KT2")
VT2 = TypeVar("VT2")
IT2 = Tuple[KT2, VT2]

SelfType = TypeVar("SelfType")  # pylint:disable=invalid-name

AllowableSourceType = Union[Iterable[IT], Mapping[KT, VT], "ImmutableDict[KT, VT]"]
InstantiationTypes = (Mapping, Iterable)  # pylint:disable=invalid-name


def immutabledict(
    iterable: Optional[AllowableSourceType] = None, *, forbid_duplicate_keys: bool = False
) -> "ImmutableDict[KT, VT]":
    """
    Create an immutable dictionary with the given mappings.

    Mappings may be specified as a sequence of key-value pairs or as another ``ImmutableDict`` or
    (on Python 3.7+ and CPython 3.6+) as a built-in ``dict``.

    If ``forbid_duplicate_keys=True`` and *iterable* contains duplicate keys, then raise ValueError.

    The iteration order of the created keys, values, and items of the resulting ``ImmutableDict``
    will match *iterable*.

    If *iterable* is already an ``ImmutableDict``, *iterable* itself will be returned.
    """
    # immutabledict() should return an empty set
    if iterable is None:
        return _EMPTY

    if isinstance(iterable, ImmutableDict):
        # if an ImmutableDict is input, we can safely just return it,
        # since the object can safely be shared.
        # It is also guaranteed not to have repeat keys
        return iterable

    if isinstance(iterable, Dict) and not DICT_ITERATION_IS_DETERMINISTIC:
        raise ValueError(
            "ImmutableDicts can only be initialized from built-in dicts when the "
            "iteration of built-in dicts is guaranteed to be deterministic (Python "
            "3.7+; CPython 3.6+)"
        )

    if not isinstance(iterable, InstantiationTypes):
        raise TypeError(
            f"Cannot create an immutabledict from {type(iterable)}, only {InstantiationTypes}"
        )

    if forbid_duplicate_keys:
        # We check for duplicate elements by comparing the original iterable length with the output
        # dict length. Some iterables don't provide a __len__ or are consumed by iteration, so we
        # listify the iterable to be safe. Calling list(dict) gets just keys, so we must grab items
        # in that case:
        if isinstance(iterable, Mapping):
            iterable = list(iterable.items())
        else:
            iterable = list(iterable)  # iterable is of key-value pairs
        original_length = len(iterable)  # must be recorded here for mypy to be happy

    ret: ImmutableDict[KT, VT] = _RegularDictBackedImmutableDict(iterable)

    if forbid_duplicate_keys and len(ret) != original_length:
        seen_once: Set[KT] = set()
        seen_twice: Set[KT] = set()
        # iterable has been made a list and so will not be consumed by iteration:
        for key, _ in iterable:
            if key not in seen_once:
                seen_once.add(key)
            else:
                seen_twice.add(key)
        # seen_twice is guaranteed to be nonempty
        raise ValueError(
            "forbid_duplicate_keys=True, but some keys "
            f"occur multiple times in input: {seen_twice}"
        )

    if ret:
        return ret
    else:
        return _EMPTY


def immutabledict_from_unique_keys(
    iterable: Optional[AllowableSourceType] = None
) -> "ImmutableDict[KT, VT]":
    """
    Create an immutable dictionary with the given mappings, but raise ValueError if
    *iterable* contains the same key twice. More information in `immutabledict`
    """
    return immutabledict(iterable, forbid_duplicate_keys=True)


class ImmutableDict(ImmutableCollection[KT], Mapping[KT, VT], metaclass=ABCMeta):
    """
    A ``Mapping`` implementation which is locally immutable.

    The hash code is computed and cached as if this map is deeply immutable.
    If this is not true, you should not use ``ImmutableDict`` as a set member or hash key.
    """

    __slots__ = ()

    # Signature of the of method varies by collection
    # pylint: disable = arguments-differ
    @staticmethod
    def of(dict_: AllowableSourceType) -> "ImmutableDict[KT, VT]":
        """
        Deprecated - prefer ``immutabledict`` module-level factory
        """
        if isinstance(dict_, ImmutableDict):
            return dict_
        else:
            return ImmutableDict.builder().put_all(dict_).build()  # type:ignore

    @staticmethod
    def empty() -> "ImmutableDict[KT, VT]":
        """
        Deprecated - prefer the ``immutabledict`` module-level factory with no arguments.
        """
        return _EMPTY

    @staticmethod
    def builder() -> "ImmutableDict.Builder[KT, VT]":
        """
        Deprecated - prefer to build a list of tuples and pass them to the ``immutabledict``
        module-level factory
        """
        return ImmutableDict.Builder()

    @staticmethod
    def index(
        items: Iterable[VT], key_function: Callable[[VT], KT]
    ) -> "ImmutableDict[KT, VT]":
        """
        Get a mapping to each value from the result of applying a key function.

        The result is an `ImmutableDict` where each given item appears as a value which
        is mapped to from the result of applying `key_function` to the value.
        """
        return immutabledict((key_function(item), item) for item in items)

    def inverse(self) -> "ImmutableDict[VT, KT]":
        """
        Get an `ImmutableDict` which is the inverse of this one.

        A key-value pair *(k,v)* will appear in the returned mapping
        if and only if *(v, k)* is in this mapping.

        If there are duplicate values in this the `ImmutableDict` *invert* is called on,
        an exception will be raised.
        """
        return immutabledict_from_unique_keys((v, k) for (k, v) in self.items())

    def modified_copy_builder(self) -> "ImmutableDict.Builder[KT, VT]":
        return ImmutableDict.Builder(source=self)

    def filter_keys(self, predicate: Callable[[KT], bool]) -> "ImmutableDict[KT, VT]":
        """
        Filters an ImmutableDict by a predicate on its keys.

        Returns an ImmutableDict just like this one but with keys for which the predicate
        returns a false value removed.

        While you can filter with a comprehension, this maintains order (or will when/if
        ImmutableDict in general is updated to maintain order) and allows us not to do any
        copying if all keys pass the filter
        """
        new_items = [item for item in self.items() if predicate(item[0])]
        if len(new_items) == len(self):
            return self
        else:
            return immutabledict(new_items)

    def __repr__(self):
        return "i" + str(self)

    def __str__(self):
        return "{%s}" % ", ".join(
            ["%s: %s" % (key.__repr__(), value.__repr__()) for key, value in self.items()]
        )

    def __reduce__(self):
        _repr = ()
        if self:
            _repr = tuple(self.items())
        return (immutabledict, (_repr,))

    class Builder(Generic[KT2, VT2]):
        def __init__(self, source: "ImmutableDict[KT2,VT2]" = None) -> None:
            self._dict: MutableMapping[KT2, VT2] = {}
            self.source = source

        def put(self: SelfType, key: KT2, val: VT2) -> SelfType:
            if self.source:
                # we only lazily copy the contents of source because if no changes are ever made
                # we can just reuse it
                # we need the temporary variable because the call to put_all below will
                # call this put method again and we need self.source to be None to avoid an
                # infinite loop
                tmp_source = self.source
                # Defend against multithreading scenario where another thread has cleared
                # self.source already. Not that this code is meant to be thread-safe anyway,
                # but at least you won't get non-deterministic crashes
                if tmp_source is not None:
                    self.source = None
                    self.put_all(tmp_source)

            self._dict[key] = val
            return self

        def put_all(
            self: SelfType, data: Union[Mapping[KT2, VT2], Iterable[IT2]]
        ) -> SelfType:
            if isinstance(data, Mapping):
                for (k, v) in data.items():
                    self.put(k, v)
            elif isinstance(data, Iterable):
                # mypy is confused
                for (k, v) in data:  # type: ignore
                    self.put(k, v)
            else:
                raise TypeError(
                    "Can only initialize ImmutableDict from another dictionary or "
                    "a sequence of key-value pairs"
                )
            return self

        def __setitem__(self, key: KT2, value: VT2) -> None:
            self.put(key, value)

        def build(self) -> "ImmutableDict[KT2, VT2]":
            if self.source:
                # if any puts were done this will be None. If no puts were done we can return
                # the ImmutableDict we were based on because we will be identical and immutable
                # objects can be safely shared
                return self.source
            if self._dict:
                return _RegularDictBackedImmutableDict(self._dict)
            else:
                return _EMPTY


class _RegularDictBackedImmutableDict(ImmutableDict[KT, VT]):
    __slots__ = ("_dict", "_hash")

    # pylint:disable=assigning-non-slot
    def __init__(self, init_dict) -> None:
        self._dict: Mapping[KT, VT] = dict(init_dict)
        self._hash: int = None

    def __getitem__(self, k: KT) -> VT:
        return self._dict.__getitem__(k)

    def __len__(self) -> int:
        return self._dict.__len__()

    def __iter__(self) -> Iterator[KT]:
        return self._dict.__iter__()

    # Could allow the Mapping ABC to do this for us, but this is more direct
    def __contains__(self, x: object) -> bool:
        return self._dict.__contains__(x)

    def __hash__(self) -> int:
        # This hashing implementation is borrowed from frozendict:
        # https://github.com/slezica/python-frozendict/blob/c5d16bafcca7b72ff3e8f40d3a9081e4c9233f1b/frozendict/__init__.py#L46
        if self._hash is None:
            h = 0
            # for key, value in self._dict.items():
            for key, value in self._dict.items():
                h ^= hash((key, value))
            self._hash = h
        return self._hash


# Singleton instance for empty
_EMPTY: ImmutableDict = _RegularDictBackedImmutableDict({})

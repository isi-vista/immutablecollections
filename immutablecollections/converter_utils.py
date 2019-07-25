from typing import Any, Iterable, Mapping, Optional, Tuple, Union

from immutablecollections import (
    ImmutableDict,
    ImmutableListMultiDict,
    ImmutableSet,
    ImmutableSetMultiDict,
    immutabledict,
    immutablelistmultidict,
    immutableset,
    immutablesetmultidict,
)


def _to_tuple(val: Iterable[Any]) -> Tuple[Any, ...]:
    """Needed until https://github.com/python/mypy/issues/5738
    and https://github.com/python-attrs/attrs/issues/519 are fixed.
    """
    return tuple(val)


def _to_immutableset(val: Optional[Iterable[Any]]) -> ImmutableSet[Any]:
    """Needed until https://github.com/python/mypy/issues/5738
        and https://github.com/python-attrs/attrs/issues/519 are fixed.
    """
    return immutableset(val)


def _to_immutabledict(
    val: Optional[
        Union[Iterable[Tuple[Any, Any]], Mapping[Any, Any], ImmutableDict[Any, Any]]
    ]
) -> ImmutableDict[Any, Any]:
    """Needed until https://github.com/python/mypy/issues/5738
        and https://github.com/python-attrs/attrs/issues/519 are fixed.
    """
    return immutabledict(val)


def _to_immutablesetmultidict(
    val: Optional[
        Union[
            Iterable[Tuple[Any, Any]], Mapping[Any, Any], ImmutableSetMultiDict[Any, Any]
        ]
    ]
) -> ImmutableSetMultiDict[Any, Any]:
    """Needed until https://github.com/python/mypy/issues/5738
        and https://github.com/python-attrs/attrs/issues/519 are fixed.
    """
    return immutablesetmultidict(val)


def _to_immutablelistmultidict(
    val: Optional[
        Union[
            Iterable[Tuple[Any, Any]], Mapping[Any, Any], ImmutableListMultiDict[Any, Any]
        ]
    ]
) -> ImmutableListMultiDict[Any, Any]:
    """Needed until https://github.com/python/mypy/issues/5738
        and https://github.com/python-attrs/attrs/issues/519 are fixed.
    """
    return immutablelistmultidict(val)

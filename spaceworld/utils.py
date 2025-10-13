"""Additional functions file in SpaceWorld."""

from collections.abc import Callable
from datetime import datetime
from functools import wraps
from inspect import signature
from typing import TypedDict, Union

from ._types import UserAny, AnnotateArgType, TupleArgs
from .errors import AnnotationsError


def annotation_depends(func: Callable[..., UserAny]) -> Callable[..., UserAny]:
    """
    Decorate for automatic dependency injection based on function annotations.

    Converts arguments according to the annotations of the function types.
    Args:
        func: A decorated function with annotations of parameter types

    Returns:
        A wrapper function with embedded dependencies
    """

    @wraps(func)
    def wrapper(*args: UserAny, **kwargs: UserAny) -> UserAny:
        """
        Annotates arguments.

        Args:
            *args (UserAny):
            **kwargs (UserAny):

        Returns:
            UserAny
        """
        from .annotation_manager import AnnotationManager
        from .parser_manager import ParserManager

        parameters = tuple(signature(func).parameters.values())
        am = AnnotationManager()
        parser = ParserManager(am)
        processed_args, processed_kwargs, _ = parser.preparing_args(
            parameters, list(args), kwargs, {}
        )
        result = func(*processed_args, **processed_kwargs)
        return result

    return wrapper


def startswith_value(value: str, sym: str) -> bool:
    """
    Determine whether a string begins and ends with a substring.

    Args:
        value (str): value
        sym (str): substring

    Returns:
        Bool
    """
    if not isinstance(value, str):
        raise ValueError(
            f"Param 'value' must be a string, resulting in: {type(value).__name__}{value}"
        )
    if not isinstance(sym, str):
        raise ValueError(
            f"Param 'sym' must be a string, resulting in: {type(sym).__name__}{sym}"
        )
    return value.startswith(sym) and value.endswith(sym)


def convert_to_bool(value: AnnotateArgType) -> bool:
    """
    Convert the value to bool.

    Args:
        value (): Argument

    Returns:
        bool object
    """
    return str(value).lower() in {"true", "yes", "y"}


def convert_to_datetime(value: AnnotateArgType) -> datetime:
    """
    Convert the argument to a datatime object.

    Args:
        value (): Argument

    Returns:
        datatime object
    """
    try:
        return datetime.fromisoformat(value)
    except ValueError as e:
        raise AnnotationsError(f"Invalid ISO date: {value}") from e


def _is_cached(
        args: TupleArgs,
        core,
        cmd: Union["BaseCommand", None],
        module: Union["BaseModule", None],
) -> bool:
    return (
            args not in core.args_cache
            or not (module and module.cached)
            or not (cmd and cmd.cached)
            or not core.cached
    )


class CommandCacheEntry(TypedDict):
    """A class for caching command arguments."""

    args: list[str] | tuple[str, ...]
    command: Union["BaseCommand", None]
    module: Union["BaseModule", None]


class BaseCommandConfig(TypedDict):
    """Class for the configuration of the command object."""

    hidden: bool  # noqa
    deprecated: bool | str  # noqa
    confirm: bool | str  # noqa
    history: bool  # noqa
    activate_modes: set[str]  # noqa
    example: str  # noqa
    big_docs: str  # noqa
    docs: str  # noqa
    is_async: None | bool  # noqa
    cached: bool  # noqa


class BaseCommandAnnotated(TypedDict, total=False):
    """Class for command cache arguments."""

    name: str
    hidden: bool  # noqa
    deprecated: bool | str  # noqa
    confirm: bool | str  # noqa
    examples: str | list[str]  # noqa
    history: bool  # noqa
    activate_modes: set[str]  # noqa
    docs: str  # noqa

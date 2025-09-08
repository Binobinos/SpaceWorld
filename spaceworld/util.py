"""Additional functions file in SpaceWorld."""

from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import TypedDict

from ._types import UserAny
from .annotation_manager import AnnotationManager


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
        parameters = tuple(signature(func).parameters.values())
        annotations = AnnotationManager()
        processed_args, processed_kwargs, _ = annotations.preparing_args(
            parameters, list(args), kwargs, {}
        )
        result = func(*processed_args, **processed_kwargs)
        return result

    return wrapper


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

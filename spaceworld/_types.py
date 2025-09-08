"""Type hints of the SpaceWorld framework."""

import inspect
from collections.abc import Callable
from typing import Any, Annotated

type UserAny = Annotated[
    Any,
    """This type means that the annotation is Any, 
    as a result of a dynamic transformation or signature of a user command or annotation.""",
]
type AnnotateArgType = Annotated[
    UserAny,
    "Any due to dynamic transformers in the annotation",
    "Returns the same or modified argument",
]

type DynamicCommand = Annotated[
    Callable[..., UserAny], "Represents any user's command with an arbitrary signature"
]

type Transformer = Annotated[
    Callable[[UserAny], UserAny],
    "The transformer object is callable. Takes one value and rotates the changed one"
    "It can serve as a validator in lambda if it returns bool",
]
type AttributeType = Annotated[type[UserAny], "Annotation for any attributes"]

type Arg = Annotated[
    str, "The CLI argument can be a positional, named flag, or Boolean flag."
]

type Args = Annotated[list[Arg], "Unprepared args. Represents a tuple of strings"]

type TupleArgs = Annotated[tuple[Arg, ...], "A tuple of untrained arguments"]

type Kwargs = Annotated[
    dict[str, bool | str | list[str]],
    "Unprepared kwargs",
    "Represents a dictionary key(str) value(bool | str) - bool for prefetching flags",
]

type NewArgs = Annotated[
    list[UserAny], "Prepared arguments by args after conversion in annotations"
]

type NewKwargs = Annotated[
    dict[str, UserAny], "Prepared arguments by kwargs after conversion in annotations"
]

type CacheType = Annotated[
    tuple[Args, NewKwargs, Kwargs], "Annotation for the argument cache"
]
type Parameter = Annotated[inspect.Parameter, "The argument parameter"]

type Parameters = Annotated[tuple[Parameter, ...], "Function signature"]

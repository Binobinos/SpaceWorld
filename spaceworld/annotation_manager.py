"""The AnnotationManager implementation is a class for annotations in SpaceWorld."""

import inspect
import types
import typing
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    get_args,
    get_origin,
    is_typeddict,
    TypedDict,
)
from uuid import UUID

from ._types import (
    AnnotateArgType,
    AttributeType,
    Transformer,
    UserAny,
)
from .errors import AnnotationsError
from .utils import convert_to_bool, convert_to_datetime


class AnnotationManager:
    """
    A class for creating a command container and annotation processing in SpaceWorld.

    Supports annotations:
        - Union annotations
        - Annotated annotations
        - Enum annotations
        - Literal annotations
        - Callable annotations, including:
            - lambda functions with the signature Callable[[Any], Any]
    """

    __slots__ = ("transformers",)

    def __init__(self) -> None:
        """
        Initialize a new module instance.

        Returns:
            None
        """
        self.transformers: dict[
            AttributeType | Transformer | UserAny | None, Transformer
        ] = {
            int: int,
            float: float,
            complex: complex,
            str: str,
            bytes: bytes,
            bytearray: bytearray,
            bool: convert_to_bool,
            Decimal: Decimal,
            datetime: convert_to_datetime,
            Path: Path,
            UUID: UUID,
            Any: lambda x: x,
            inspect.Parameter.empty: lambda x: x,
            None: lambda x: x,
        }

    def add_custom_transformer(
        self, type_: AttributeType, transformer: Transformer
    ) -> Transformer:
        """
        Add a custom handler for annotations.

        Args:
            type_ (): The type in the annotation
            transformer (): Handler

        Return:
            Handler's return.
        """
        if not callable(transformer):
            raise ValueError(
                f"Transformer must be a callable object, obtained by {type_(transformer)}"
            )
        if not isinstance(type_, type):
            raise ValueError(
                f"Type transformer must be a class, obtained by {type_(type_)}"
            )
        if type_ in self.transformers:
            raise ValueError(f"Transformer for {type_} already exists")
        self.transformers[type_] = transformer
        return self.transformers[type_]

    def annotate(
        self, annotation: AttributeType, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Convert the annotation argument to the final value.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        origin = get_origin(annotation)
        match origin:
            case types.UnionType | typing.Union:
                return self._annotate_union(annotation, arg)
            case typing.Annotated:
                return self._annotate_annotated(annotation, arg)
            case typing.Literal:
                return self._validate_literal(annotation, arg)
            case None:
                return self._annotate_base_type(annotation, arg)
            case _:
                raise AnnotationsError(f"Unsupported type {annotation}")

    def _annotate_union(
        self, annotation: AttributeType, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Annotate the Union type.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        errors = []
        for param_type in get_args(annotation):
            try:
                arg = self.annotate(param_type, arg)
                return arg
            except AnnotationsError as error:
                errors.append(error)
        errors_mes = [
            f"- {num} Error: {error}" for num, error in enumerate(errors, start=1)
        ]
        message = f"None of the types in the Union are suitable. List of errors: {f'\n\t{"\n\t".join(errors_mes)}'}"
        raise AnnotationsError(message) from errors[-1]

    def _annotate_annotated(
        self, annotation: AttributeType, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Annotate the Annotated type.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        for index, param_type in enumerate(get_args(annotation)):
            try:
                arg = self.annotate(param_type, arg)
            except Exception as error:
                message = f"Error in the Annotated with an index '{index}', validation for '{arg}': {error}, {type(error)}"
                raise AnnotationsError(message) from error
        return arg

    def _annotate_callable(
            self, func: Transformer, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Annotate callable objects.

        Args:
            func(): A callable object
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        try:
            if func.__name__ == "<lambda>":
                return self._annotate_lambda(func, arg)
            return func(arg) or arg
        except Exception as error:
            raise AnnotationsError(f"Arg: '{arg}', Error: {error}") from error

    def _annotate_typed_dict(
            self, annotation: type[TypedDict], arg: dict[str, Any]
    ) -> dict[str, Any]:
        new_items = {}
        for name, annotation in annotation.__annotations__.items():
            value = arg.get(name)
            if value is None:
                continue
            if get_origin(annotation) in {typing.Required, typing.NotRequired}:
                annotation = get_args(annotation)[0]
            new_items[name] = self.annotate(annotation, value)
        return new_items

    def _annotate_base_type(
        self, annotation: AttributeType, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Annotate the basic types.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        transformers = self.transformers
        if annotation in transformers:
            func = transformers[annotation]
            try:
                return func(arg)
            except Exception as error:
                raise AnnotationsError(
                    f"Couldn't convert to '{func.__name__}': {error}"
                ) from error
        return self._annotate_normal_type(annotation, arg)

    def _annotate_normal_type(
        self, annotation: AttributeType, arg: AnnotateArgType
    ) -> AnnotateArgType:
        """
        Annotate basic types and callable objects.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        if isinstance(annotation, str):
            return arg
        if is_typeddict(annotation):
            if not isinstance(arg, dict):
                arg = self.annotate(dict, arg)
            self._validate_typed_dict(annotation, arg)
            return self._annotate_typed_dict(annotation, arg)
        if callable(annotation):
            return self._annotate_callable(annotation, arg)
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return self._validate_enum(annotation, arg)
        raise AnnotationsError(f"Unsupported type in the annotation:{annotation}")

    @staticmethod
    def _annotate_lambda(func: Transformer, arg: AnnotateArgType) -> AnnotateArgType:
        """
        Annotate lambda.

        Args:
            arg(): argument
            func(): lambda function

        Returns:
            the final value
        """
        value = func(arg)
        if isinstance(value, BaseException):
            raise AnnotationsError(str(value)) from value
        if value is False:
            raise AnnotationsError(
                f"Failed validation for '{arg}' in the lambda function"
            )
        if isinstance(value, bool) and not isinstance(arg, bool):
            return arg
        return value

    @staticmethod
    def _validate_enum[T](annotation: type[Enum], arg: T) -> T:
        """
        Annotate Enum and string annotations.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final argument
        """
        valid_values = {e.value for e in annotation}
        if arg in valid_values:
            return annotation(arg)
        message = (
            f"The value of '{arg}' does not match the Enum[{'/'.join(valid_values)}]"
        )
        raise AnnotationsError(message)

    @staticmethod
    def _validate_literal[T](annotation: type[typing.Literal], arg: T) -> T:
        """
        Annotate the Literal type.

        Args:
            annotation (): Annotation
            arg(): Argument

        Returns:
            The final value after the transformations
        """
        args = get_args(annotation)
        if arg in args:
            return arg
        message = f"The value of '{arg}' does not match Literal['{"'/'".join(args)}']"
        raise AnnotationsError(message)

    @staticmethod
    def _validate_typed_dict[T: dict[str, Any]](
            annotation: type[TypedDict], arg: T
    ) -> T:
        items = arg.copy()
        errors = []
        for name in annotation.__required_keys__:
            if name in items:
                del items[name]
                continue
            errors.append(f"The required key '{name}' is missing")
        for name in annotation.__optional_keys__:
            if name in items:
                del items[name]
        if items:
            extra_keys = "\n - ".join(
                f"'{name}': '{value}'" for name, value in items.items()
            )
            errors.append(f"Extra keys: \n - {extra_keys}")
        if errors:
            raise ValueError("\n - ".join(errors))
        return arg

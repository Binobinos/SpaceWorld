from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction, run, get_running_loop
from inspect import signature
from typing import Unpack

from ._types import Parameters, UserAny, Args, DynamicCommand
from .util import BaseCommandAnnotated, BaseCommandConfig


class Command(ABC):
    __slots__ = (
        "name",
        "aliases",
        "func",
        "config",
        "_examples",
        "_example",
        "_parameters",
        "_help_text",
        "_is_async",
    )

    def __init__(
        self,
        *,
        aliases: Args | None = None,
        func: DynamicCommand | None,
        big_docs: str | None = None,
        **opt: Unpack[BaseCommandAnnotated],
    ):
        """
        Initialize a new command instance.

        Args:
            name: Command name (defaults to function name)
            aliases: Alternative command names
            docs: Short description (defaults to function docstring)
            examples: Usage example (auto-generated if empty)
            activate_modes: Valid activation modes (default: ["normal"])
            func: Command implementation function
            big_docs: Detailed documentation (defaults to short docs)
            hidden: If True, hides from help/autocomplete
            deprecated: Deprecation flag or custom message
            confirm: Confirmation requirement flag or custom prompt
            history: If False, excludes from command history
        """
        self.func: DynamicCommand | None = func
        self.name: str = opt.get("name") or (
            self.func.__name__ if self.func is not None else ""
        )
        docs = opt.get("docs") or (self.func.__doc__ if self.func is not None else "")
        self.aliases: Args = aliases or []
        self._examples = opt.get("examples", "")

        self.config: BaseCommandConfig = {
            "activate_modes": opt.get("activate_modes", {"normal"}),
            "hidden": opt.get("hidden", False),
            "deprecated": opt.get("deprecated", False),
            "big_docs": big_docs or docs or "",
            "confirm": opt.get("confirm", ""),
            "history": opt.get("history", True),
            "is_async": None,
            "docs": docs or "",
            "cached": opt.get("cached", True),
        }
        self._parameters: Parameters | None = None
        self._help_text: str | None = None
        self._example: str | None = None
        self._is_async: bool | None = None

    @property
    def big_docs(self) -> str:
        """
        Return a large documentation on the function.

        Returns:
            returns the docs
        """
        return self.config["big_docs"]

    @property
    def cached(self) -> bool:
        """
        Returns the caching value of the function.

        Returns:
            bool
        """
        return self.config["cached"]

    @property
    def is_async(self) -> bool:
        """Check if command is asynchronous."""
        if self.func is None:
            raise RuntimeError("The function is not defined")
        if self._is_async is None:
            self._is_async = iscoroutinefunction(self.func)
        return self._is_async

    @property
    def parameters(self) -> Parameters:
        """Get function parameters signature."""
        if self.func is None:
            raise RuntimeError("The function is not defined")
        if self._parameters is None:
            self._parameters = tuple(signature(self.func).parameters.values())
        return self._parameters

    @property
    def help_text(self) -> str:
        """Get formatted help documentation."""
        if self._help_text is None:
            self._help_text = self.get_help_doc()
        return self._help_text

    @property
    def examples(self) -> str:
        """Get usage examples."""
        if self._example is None:
            self._example = self.generate_example(self._examples)
        return self._example

    @abstractmethod
    def get_help_doc(self) -> str:
        """Generate formatted help documentation for the command."""

    @abstractmethod
    def generate_example(self, examples: str | Args) -> str:
        """Generate documentation for the team."""

    def __call__(self, *args: UserAny, **kwargs: UserAny) -> UserAny:
        """
        Run func.

        Args:
            *args ():
            **kwargs ():

        Returns:
            None
        """
        if self.func is None:
            raise RuntimeError("The function is not defined")
        if not self.is_async:
            return self.func(*args, **kwargs)

        coroutine = self.func(*args, **kwargs)
        try:
            loop = get_running_loop()
        except RuntimeError:
            return run(coroutine)

        return loop.run_until_complete(coroutine)

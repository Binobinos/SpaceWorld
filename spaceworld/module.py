from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Unpack, Self

from ._types import Args, DynamicCommand, UserAny, Transformer
from .command import Command
from .command_error import CommandCreateError
from .module_error import ModuleCreateError
from .util import BaseCommandAnnotated


class Module(Command, ABC):
    __slots__ = (
        "docs",
        "commands",
        "modules",
    )

    def __init__(
        self,
        *,
        func: DynamicCommand | None,
        aliases: Args | None = None,
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
        from .base_command import BaseCommand
        from .base_module import BaseModule

        super().__init__(func=func, aliases=aliases, big_docs=big_docs, **opt)
        self.commands: dict[str, BaseCommand] = {}
        self.modules: dict[str, BaseModule] = {}
        self.docs = self.config["docs"]

    def spaceworld(self, target: type[UserAny] | DynamicCommand) -> UserAny:
        """
        Register a callable or class as commands in SpaceWorld.

        This method automatically handles registration of:
        - Classes as modules (converting methods to commands)
        - Callable objects as individual commands

        Args:
            target: Either:
                    - A class (converted to module with command methods)
                    - A callable object (registered as single command)

        Behavior:
            For classes:
            - Creates a BaseModule with the class name
            - Registers all non-private methods as commands
            - Skips methods starting with '_'

            For callables:
            - Registers the function directly as a command

        Notes:
            - Class methods become commands under their original names
            - The decorator can be used both on classes and functions
            - Private methods (starting with _) are ignored
        """

        from spaceworld.base_module import BaseModule

        module = BaseModule(name=target.__name__, func=None)
        return self.register(
            target=target,
            module=module,
        )

    def register(
            self,
            target: type[UserAny] | DynamicCommand,
            module: UserAny,
    ) -> UserAny | DynamicCommand:
        """
        Register a callable or class as commands or submodule in SpaceWorld.

        This method automatically handles registration of:
            - Classes as modules or submodule (converting methods to commands)
            - Callable objects as individual commands

            Args:
                module ():
                target: Either:
                        - A class (converted to module with command methods)
                        - A callable object (registered as single command)

            Behavior:
                For classes:
                - Creates a BaseModule with the class name
                - Registers all non-private methods as commands
                - Skips methods starting with '_'

                For callables:
                - Registers the function directly as a command
            Notes:
                - Class methods become commands under their original names
                - The decorator can be used both on classes and functions
                - Private methods (starting with _) are ignored
        """
        if hasattr(target, "__bases__") and hasattr(target, "__mro__"):
            self._submodule(module)
            for name in dir(target):
                if name.startswith("_"):
                    module.decorator(getattr(target, name))
            return target
        return self._register_command(target)

    def module(
        self,
        *args: DynamicCommand | UserAny,
        **kwargs: Unpack[BaseCommandAnnotated],
    ) -> Callable[[DynamicCommand], Self] | Self:
        """
        Create a submodule.

        It serves as a wrapper over the decorator to support decorators with and without arguments.
        if only one args element is passed,
        it will return the submodule object, otherwise the decorator

        Args:
            *args(): Positional arguments for the decorator or a single function
            **kwargs(): Named arguments

        Returns:
            Submodule Object or Decorator
        """
        from .base_module import BaseModule

        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            func: DynamicCommand = args[0]
            name = func.__name__
            return self._submodule(module=BaseModule(name=name, func=func))

        def decorator(func: DynamicCommand) -> Any:
            """
            Register and returns the SubModule.

            Args:
                func(): SubModule

            Returns:
                The same SubModule
            """
            return self._submodule(module=BaseModule(func=func, **kwargs))

        return decorator

    def command(
        self,
        *,
        aliases: Args | None = None,
        big_docs: str | None = None,
        **kwargs: Unpack[BaseCommandAnnotated],
    ) -> Transformer:
        """
        Decorate that registers a function as a configured command.

        Args:
            big_docs ():
            aliases: List of command aliases

        Returns:
            Command registration decorator

        Raises:
            CommandCreateError: If command or aliases already exists
        """
        from .base_command import BaseCommand

        if aliases is None:
            aliases = []

        def decorator(func: DynamicCommand) -> DynamicCommand:
            """
            Register a function with arguments.

            Args:
                func(): Function

            Returns:
                Function
            """
            name = kwargs.get("name")
            func_name = name.replace("-", "_") if name else func.__name__
            names = aliases + [func_name]
            existing = [name for name in names if name in self.commands]
            if existing:
                raise CommandCreateError(f"Command '{'/'.join(names)} already exists")
            command = BaseCommand(
                aliases=aliases, big_docs=big_docs, func=func, **kwargs
            )
            for alias in names:
                self.commands[alias] = command
            return func

        return decorator

    def _submodule(self, module: Self) -> Self:
        """
        Register a submodule within this module.

        Args:
            module: BaseModule instance to register

        Raises:
            SubModuleCreateError: If submodule name already exists
        """
        from .base_module import BaseModule

        name = module.name
        if not isinstance(module, BaseModule) or name in self.modules:
            raise ModuleCreateError(f"Submodule '{name}' already exists")
        self.modules[name] = module
        return module

    def _register_command(self, func: DynamicCommand) -> DynamicCommand:
        """
        Register the team in SpaceWorld.

        Creates a basic BaseCommand wrapper around the function with default settings:
        - Command name matches function name
        - Active in all modes
        - No aliases or special configurations

        Args:
            func: The callable to register as a command. Must have a __name__ attribute.

        Raises:
            CommandCreateError: If a command with the same name already exists.

        Notes:
            - This is an internal method typically called by other registration decorators
            - For more control over command properties, use the @command decorator instead
            - The created command will be active in all operation modes ('all')
        """
        from .base_command import BaseCommand

        func_name = func.__name__
        if func_name in self.commands:
            raise CommandCreateError(f"Command '{func_name}' already exists")
        self.commands[func_name] = BaseCommand(name=func_name, func=func)
        return func

    @abstractmethod
    def get_help_doc(self) -> str:
        """Generate formatted help documentation for the command."""

    def generate_example(self, examples: str | Args) -> str:
        """Generate documentation for the team."""
        if not self.modules and self.commands:
            name = "COMMAND"
        elif self.modules and not self.commands:
            name = "SUBMODULE"
        else:
            name = "COMMAND/SUBMODULE"
        examples = "\n".join(examples) if isinstance(examples, list) else examples
        return f"{self.name} [{name}] [ARGS] [OPTIONS] \n{examples}"

    def include(  # noqa
            self, obj: Callable[..., UserAny]
    ) -> Callable[..., UserAny]:
        """Add modules to the SpaceWorld environment.

        This method can either:
        - Import Python packages from a directory when given a Path object
        - Directly register module instances when provided in a list/tuple

        Args:
            obj: Either:
                    - A pathlib.Path object pointing to a directory of Python modules
                    - A list or tuple of pre-initialized BaseModule instances

        Behavior:
            - When given a Path:
                * Creates the directory if it doesn't exist
                * Attempts to import all .py files in the directory as modules
                * Silently skips files that fail to import or register
            - When given a list/tuple:
                * Directly registers each provided module

        Returns:
            The input object after processing (for method chaining)

        Notes:
            - For directory imports:
                * Only .py files are processed
                * The directory becomes a Python package
                * Modules must implement a register() function
            - Invalid modules are silently ignored
        """
        from .base_module import BaseModule
        from .spaceworld_cli import SpaceWorld

        if isinstance(obj, BaseModule):
            self._submodule(obj)
            return obj
        if callable(obj):
            self._register_command(obj)
            return obj
        if isinstance(obj, SpaceWorld):
            self.modules |= obj.modules
            self.commands |= obj.commands
            if isinstance(self, SpaceWorld):
                self.di.transformers |= obj.di.transformers
            return obj
        raise TypeError(f"Dont Support Type: {type(obj)}")

    def run_command(self, *args: UserAny, **kwargs: UserAny) -> UserAny:
        """Execute the module's function if it exists."""
        if self.func is None:
            raise RuntimeError("The function is not defined")
        return super().__call__(*args, **kwargs)

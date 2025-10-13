"""The main module Of SpaceWorld That implements the basic logic of the framework."""

import inspect
import shlex
import sys
from collections.abc import Callable
from typing import Never, Unpack, override

from ._types import (
    Args,
    CacheType,
    DynamicCommand,
    Kwargs,
    NewKwargs,
    TupleArgs,
    UserAny,
    AttributeType,
)
from .annotation_manager import AnnotationManager
from .base_command import BaseCommand
from .base_module import BaseModule
from .errors import ExitError, AnnotationsError
from .module import Module
from .parser_manager import ParserManager
from .utils import BaseCommandAnnotated, CommandCacheEntry, _is_cached
from .writer import Writer


class SpaceWorld(Module):
    """The main class of the SpaceWorld Framework."""

    __slots__ = (
        "am",
        "command_history",
        "writer",
        "_confirmation_command",
        "command_cache",
        "handlers",
        "version",
        "system_flags",
        "_options_help",
        "_errors_help",
        "args_cache",
        "parser",
    )

    def __init__(
            self,
            writer: Writer | None = None,
            annotations_manager: AnnotationManager | None = None,
            parser: ParserManager | None = None,
            *,
            version: str = "",
            func: DynamicCommand | None = None,
            **opt: Unpack[BaseCommandAnnotated],
    ) -> None:
        """
        Initialize the SpaceWorld instance.

        Args:
            writer: An optional Writer class instance or its subclass for output operations.
                   If not provided, a default MyWriter instance will be used.

        Attributes initialized:
            annotations (Dict[str, Any]): A dictionary for storing arbitrary annotations.
            writer (Writer): The writer instance used for output operations.
            mode (str): Current operation mode (default: "normal").
            waiting_for_confirmation (bool): Flag indicating if waiting for user confirmation.
            confirm_message (list[str] | None): Message to display when confirmation is needed.
            _confirmation_command (str | None): Command to execute upon confirmation.
            command_cache (Dict[str, dict[str, BaseCommand | list[str]] | bool]):
                Cache for command data.
            args_cache (Dict[tuple, tuple]): Cache for command arguments.
            commands (Dict[str, BaseCommand]): Registered commands.
            modules (Dict[str, BaseModule]): Loaded modules.

        Notes:
            - Automatically adds annotations for self and the writer instance.
            - Uses MyWriter as default if no writer is provided.
        """
        super().__init__(func=func, **opt)
        self.version: str = version
        self.handlers: dict[str, Callable[..., None | ExitError | UserAny | Never]] = {}
        self.command_cache: dict[TupleArgs, CommandCacheEntry] = {}
        self.args_cache: dict[TupleArgs, CacheType] = {}
        self.system_flags: set[str] = set()
        self._options_help = []
        self._errors_help = []
        self.am: AnnotationManager = annotations_manager or AnnotationManager()
        self.parser = parser or ParserManager(self.am)
        self.writer: Writer = writer or Writer()
        self._confirmation_command: TupleArgs | None = None
        self.am.add_custom_transformer(SpaceWorld, lambda _: self)
        self.am.add_custom_transformer(Writer, lambda _: self.writer)
        self.handler(name="deprecated")(self._write_deprecated)
        self.handler(name="error")(self._handle_error)
        self.handler(name="confirm")(self._handle_confirmation)
        self._add_system_flag(
            "help/h", "Displays a help message", "help", self._write_help
        )
        self._add_system_flag(
            "version/v",
            "Displays the application version",
            "version",
            self.version_handler,
        )
        self._add_system_flag(
            "force/f", "Enables confirm mode", "force", self._handle_confirm
        )

    def transformer(
            self, type_: AttributeType
    ) -> Callable[[DynamicCommand], DynamicCommand]:
        def wrap(transformer: DynamicCommand) -> DynamicCommand:
            self.am.add_custom_transformer(type_, transformer)
            return transformer

        return wrap

    def system_flag(
            self, name: str, docs: str, handler_name: str
    ) -> Callable[[DynamicCommand], DynamicCommand]:
        if not any(isinstance(atr, str) for atr in {name, docs, handler_name}):
            raise ValueError("All attributes must be string")

        def wrap(handler: DynamicCommand) -> DynamicCommand:
            self._add_system_flag(name, docs, handler_name, handler)
            return handler

        return wrap

    def error_handler(
            self,
            error: type[Exception],
            docs: str,
    ) -> Callable[[DynamicCommand], DynamicCommand]:
        """
        Handle errors and outputs a message.

        Args:
            docs ():
            error (type[Exception]): Type of error

        Returns:
            None
        """
        if not isinstance(error, BaseException):
            raise ValueError("Param 'error' must be instance Exception")
        if not isinstance(docs, str):
            raise ValueError("Param 'docs' must be instance Exception")
        name = error.__name__

        def wrap(func):
            self.handler(name=f"errors.{name}")(func)

            return func

        self._errors_help.append(
            f"  {error}{f' - {docs.strip().title()}' if docs else ''}"
        )
        return wrap

    def version_handler(
            self,
            kwargs: Kwargs | NewKwargs,
            cmd: BaseCommand | None,
            module: BaseModule | None,
    ) -> None:
        """
        Handle errors and outputs a message.

        Returns:
            None
        """
        if kwargs.get("version", False) or kwargs.get("v", False):
            self.writer.write(
                f"{self.name.title()} version: {self.version.strip() if self.version.strip() else ''}"
            )
            raise ExitError

    def handler(
            self, *args: DynamicCommand | UserAny, **kwargs: UserAny
    ) -> Callable[[DynamicCommand], DynamicCommand] | DynamicCommand:
        """
        Create a module.

        It serves as a wrapper over the decorator to support decorators with and without arguments.
        if only one args element is passed,it returns the modified function, otherwise the decorator
        Args:
            *args (Callable | Any): Positional arguments for the decorator or a single function
            **kwargs (Any): Named arguments

        Returns:
            Function or Decorator
        """
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            handler: DynamicCommand = args[0]
            name = kwargs.get("name", handler.__name__)
            self.handlers[name] = handler
            return handler

        def _wraps(handler: DynamicCommand) -> DynamicCommand:
            """
            Register a function with arguments.

            Args:
                handler(): Function

            Returns:
                Function
            """
            name = kwargs.get("name", handler.__name__)
            self.handlers[name] = handler
            return handler

        return _wraps

    def _add_system_flag(
            self, name: str, docs: str, handler_name: str, handler: DynamicCommand
    ):
        name, _, short_name = name.strip().partition("/")
        self._options_help.append(
            f"  --{name}{f' -{short_name}' if short_name else ''} - {docs}"
        )
        self.system_flags.add(name)
        self.system_flags.add(short_name)
        self.handler(name=handler_name)(handler)

    def _get_args_info(self) -> str:
        """
        Format parameter information for help documentation.

        Returns:
            str: Formatted parameter details with:
                 - Parameter names
                 - Types
                 - Default values
        """
        return "\n".join(
            [
                f"  {prm.name}: {prm.annotation.__name__}"
                for prm in self.parameters
                if prm.kind not in {prm.KEYWORD_ONLY, prm.VAR_KEYWORD}
                   and prm.annotation is not bool
            ]
        )

    def _get_options_info(self) -> str:
        """
        Format parameter information for help documentation.

        Returns:
            str: Formatted parameter details with:
                 - Parameter names
                 - Types
                 - Default values
        """
        emp = inspect._empty
        options: list[str] = self._options_help + [
            (
                f"  --{prm.name.replace('_', '-')}: "
                f"{name if (name := prm.annotation.__name__) != emp else 'Any'} "
                f"{f'= {default}' if (default := prm.default) != emp else ''}"
            )
            for prm in self.parameters
            if prm.kind in {prm.KEYWORD_ONLY, prm.VAR_KEYWORD} or prm.annotation is bool
        ]
        return "\n\t".join(options)

    @override
    def get_help_doc(self) -> str:
        """Generate formatted help documentation for the command."""
        examples_command = "\n\t".join(
            f"{cmd.examples}\t{cmd.config['docs'].strip()}"
            for cmd in self.commands.values()
        )
        examples_module = "\n\t".join(
            f"{cmd.examples}\t{cmd.config['docs'].strip()}"
            for cmd in self.modules.values()
        )
        msg = f"\n\t{examples_command}"
        msg_ = f"\n\t{examples_module}"
        args = self._get_args_info()
        return (
            f"{self.name} "
            f"{f'- {self.docs.strip()} ' if self.docs.strip() else ''}"
            f"{self.version if self.version.strip() else ''}\n\n"
            f"{f'Commands: {msg}\n\t' if msg.strip() else ''}"
            f"{f'Modules: {msg_}\n\t' if msg_.strip() else ''}"
            f"{f'Args: \n{args}\n\n' if args else ''}\n"
            f"Options: \n\t{self._get_options_info()}\n"
            f"{f'Error Handler:\n\t{"\n\t".join(self._errors_help)}' if self._errors_help else ''}"
        )

    def _handle_error(self, error: type[Exception]):
        try:
            self.get_handler(f"errors.{type(error).__name__}")()
        except Exception:
            self.writer.error(f"Error when executing the command: {str(error)}")

    def get_handler(self, name: str) -> DynamicCommand:
        """
        Return a handler object by name.

        Args:
            name (str): handler's name

        Returns:
            handler's object
        """
        if not isinstance(name, str):
            raise ValueError("Name handler must be string")
        if name not in self.handlers:
            raise KeyError(f"Handler {name} not found")
        return self.handlers[name]

    def execute(self, command: TupleArgs | Args) -> UserAny | None:
        """
        Execute a console command in the SpaceWorld environment.

        Handles command execution with the following features:
        - Empty command validation
        - Pending confirmation handling
        - Error reporting for invalid commands
        - Normal command execution flow

        Args:
            command: The command string to execute. If empty, shows an error.

        Behavior:
            1. Validates the command is a non-empty string
            2. Checks for pending confirmations (handles them first if found)
            3. Executes the command through execute_command()
            4. Handles command execution results:
               - None or False indicates invalid command
               - True indicates successful execution
        """
        try:
            if self._confirmation_command:
                return self.get_handler("confirm")(command)
            return self.execute_command(command)
        except ExitError:
            return None
        except Exception as error:  # pylint: disable=W0718 # User Function
            self.get_handler("error")(error)
            return None

    def execute_command(
        self, command: TupleArgs | Args, *, confirmation: bool | str = False
    ) -> UserAny | ExitError:
        """
        Execute a SpaceWorld command with full argument processing and validation.

        Handles the complete command execution pipeline including:
        - Command lookup and caching
        - Argument parsing and preparation
        - Mode validation
        - Help flag handling
        - Deprecation warnings
        - Confirmation flow
        - Error handling

        Args:
            command (): The command string to execute (including arguments)
            confirmation: Bypass confirmation prompt if True (default: False)

        Returns:
            bool | None:
                - True if command executed successfully
                - False if command not found or mode mismatch
                - None if execution failed or requires confirmation

        Behavior:
            1. Checks command cache or performs new command search
            2. Validates command is available in current mode
            3. Processes arguments (cached if previously parsed)
            4. Handles help flags (--help/-h) by showing command documentation
            5. Manages deprecation warnings
            6. Handles confirmation requirements
            7. Executes command with prepared arguments
            8. Returns execution status
        Notes:
            - Uses LRU caching for command lookup and argument parsing
            - Automatically handles --help/-h flags
            - Respects command activation modes
            - Manages deprecation warnings
            - Requires confirmation for sensitive commands unless bypassed
        """
        commands: CommandCacheEntry = self._get_command_cache(command)
        args: TupleArgs = tuple(commands["args"])
        cmd: BaseCommand | None = commands["command"]
        module: BaseModule | None = commands["module"]

        positional_args, keyword_args, kwargs = self._get_cached_args(args, cmd, module)
        self.get_handler("help")(kwargs, cmd, module)
        self.get_handler("version")(kwargs, cmd, module)

        confirmation = kwargs.get("force", confirmation)
        self.get_handler("force")(cmd, confirmation, command)
        self.get_handler("deprecated")(cmd)
        if cmd is None:
            cmd: DynamicCommand = module.run_command if module else None
            if cmd is None:
                if self.func is None:
                    self.writer.write(self.help_text)
                    raise ExitError
                cmd = self.run_command
        return cmd(*positional_args, **keyword_args)

    def run(
            self, func: DynamicCommand | None = None, args: Args | None = None
    ) -> UserAny | None:
        """
        Start the main Execution cycle for the SpaceWorld console environment.

        Handles both direct command execution and interactive console operation:
        - Registers commands/functions when provided
        - Processes command-line arguments
        - Manages confirmation prompts
        - Maintains interactive session until completion

        Args:
            func: Optional callable to register as a command before execution
            args: Command arguments (defaults to sys.argv[1:] if None)

        Behavior:
            1. Registers provided function (if any) using spaceworld decorator
            2. Executes command from arguments (joins list into string)
            3. Enters interactive confirmation loop if needed:
               - Prompts for user input
               - Processes responses through execute()
               - Continues until confirmation is resolved

        Notes:
            - Defaults to system arguments if none provided
            - Handles both single commands and interactive sessions
            - Maintains full command processing pipeline
            - Supports SpaceWorld's confirmation workflow
        """
        if func:
            self.spaceworld(func)
        if args is None:
            args = sys.argv[1:]
        try:
            result = self.execute(args)
            while self._confirmation_command:
                user_input = input(">>> ")
                result = self.execute(shlex.split(user_input))
            return result
        except KeyboardInterrupt:
            sys.exit(-1)

    def _write_help(
        self,
        kwargs: Kwargs | NewKwargs,
        cmd: BaseCommand | None,
        module: BaseModule | None,
    ) -> None:
        """
        Output help if there are keys in the dictionary.

        Args:
            kwargs (): Dictionary

        Returns:
            True if the help is displayed, False if not
        """
        if kwargs.get("help", False) or kwargs.get("h", False):
            help_text: str = (
                cmd.help_text if cmd else module.help_text if module else self.help_text
            )
            self.writer.write(help_text)
            raise ExitError

    def _handle_confirm(
        self, cmd: BaseCommand, confirmation: bool, command: TupleArgs
    ) -> None:
        if cmd and cmd.config["confirm"] and not confirmation:
            self._set_confirm_command(command, cmd)
            raise ExitError

    def _get_command_cache(self, args: TupleArgs | Args) -> CommandCacheEntry:
        """
        Return cached arguments for later invocation.

        Args:
            args (tuple[str, ...]): Bare arguments

        Returns:
            Ready-made cached arguments
        """
        args = tuple(args)
        if args not in self.command_cache:
            self.command_cache[args] = self.parser.search_command(args, self)
        return self.command_cache[args]

    def _write_deprecated(self, cmd: BaseCommand) -> None:
        """
        Output a warning command.

        Args:
            cmd(): Command object
        Returns:
            None
        """
        if cmd and (deprecated := cmd.config["deprecated"]):
            self.writer.warning(deprecated)

    def _get_cached_args(
        self, args: TupleArgs, cmd: None | BaseCommand, module: None | BaseModule
    ) -> CacheType:
        """
        Return cacheable arguments.

        Args:
            args (): Bare arguments
            cmd(): Command object
        Raises:
            TypeError: Exit with None
            ValueError: The help table is displayed and returns with True
        Returns:
            A tuple of new args and kwargs and naked kwargs
        """
        if _is_cached(args, self, cmd, module):
            kwargs: dict[str, bool | str] = {}
            try:
                parameters = (
                    cmd.parameters
                    if cmd
                    else module.parameters
                    if module
                    else self.parameters
                )

                positional_args, kwargs = self.parser.pre_preparing_arg(
                    args, parameters, self.system_flags
                )
                self.get_handler("help")(kwargs, cmd, module)
                self.args_cache[args] = self.parser.preparing_args(
                    parameters, positional_args, kwargs, self.system_flags
                )
            except (ValueError, IndexError, TypeError, AnnotationsError) as error:
                self.get_handler("help")(kwargs, cmd, module)
                self.get_handler("error")(error)
                raise ExitError from error
        return self.args_cache[args]

    def _handle_confirmation(self, response: TupleArgs | Args) -> None:
        """
        Handle user confirmation responses for sensitive commands.

        Processes the user's response to a confirmation prompt and either:
        - Executes the pending command (if confirmed)
        - Cancels the operation (if denied)

        Args:
            response: User's input response to the confirmation prompt
        Behavior:
            - Compares response against valid confirmation words (case-sensitive)
            - On confirmation:
              * Logs the execution
              * Executes the pending command with confirmation bypass
            - On denial:
              * Cancels the operation with warning
            - Always resets confirmation state after handling
        Side Effects:
            - Modifies instance state:
              * waiting_for_confirmation (set to False)
              * _confirmation_command (set to None)
            - May execute pending command
            - Writes to output via writer
        """
        if response[0].lower() in {"yes", "y"}:
            result = self.execute_command(self._confirmation_command, confirmation=True)
            self._confirmation_command = None
            return result
        self._confirmation_command = None
        self.writer.warning("The command has been cancelled.")
        raise ExitError

    def _set_confirm_command(self, command: TupleArgs, func: BaseCommand) -> None:
        """
        Set up a command confirmation prompt in the SpaceWorld environment.

        Prepares the system for command confirmation by:
        - Displaying the confirmation prompt message
        - Setting the command in pending confirmation state
        - Storing the confirmation requirements

        Args:
            command: The full command string awaiting confirmation
            func: The BaseCommand instance requiring confirmation

        Side Effects:
            - Stores command as _confirmation_command
            - Sets confirm_message from command's confirm_word
            - Displays prompt to user via writer

        Behavior:
            - Uses custom confirmation message if specified in command
            - Falls back to default message if no custom message provided
            - Puts system in confirmation state until user responds

        Notes:
            - Actual confirmation handling occurs in _handle_confirmation
            - System remains in confirmation state until user responds
            - Command won't execute until confirmed
        """
        self.writer.input(func.config["confirm"])
        self._confirmation_command = command

    @override
    def __call__(
            self, func: DynamicCommand | None = None, args: Args | None = None
    ) -> UserAny | None:
        """
        Call run of the class.

        It is used for convenient calling
        Args:
            func(): A callable object
            args(): Arguments to call from the code

        Returns:
            None
        """
        return self.run(func, args)


def run(func: DynamicCommand | None = None, args: Args | None = None) -> UserAny | None:
    """
    Initialize and runs a SpaceWorld console session.

    This is the main entry point for executing commands in a SpaceWorld environment.
    It handles both direct command execution and interactive sessions with confirmations.

    Args:
        func: A callable to register as a command before execution (optional).
              If provided, will be decorated with @spaceworld.
        args: List of command arguments as strings (optional).
              Defaults to sys.argv[1:] if None (command line arguments).

    Behavior:
        1. Creates a new SpaceWorld instance
        2. Registers the provided function (if any)
        3. Executes the command from arguments
        4. Enters interactive confirmation loop if needed:
           - Shows prompt (> )
           - Processes user input
           - Continues until confirmation is resolved

    Notes:
        - Creates a fresh SpaceWorld instance for each run
        - Supports both programmatic and command-line usage
        - Handles the complete command lifecycle including confirmations
        - Default prompt for confirmations is '> '
    """
    return SpaceWorld(func=func).run(func, args)


def spaceworld(
        *args: DynamicCommand | UserAny,
        version: str = "",
        **kwargs: Unpack[BaseCommandAnnotated],
) -> Callable[[DynamicCommand], SpaceWorld] | SpaceWorld:
    """
    Create a submodule.

    It serves as a wrapper over the decorator to support decorators with and without arguments.
    if only one args element is passed,
    it will return the submodule object, otherwise the decorator

    Args:
        version ():
        *args(): Positional arguments for the decorator or a single function
        **kwargs(): Named arguments

    Returns:
        Submodule Object or Decorator
    """

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        func: DynamicCommand = args[0]
        return SpaceWorld(func=func, version=version)

    def wrap(func: DynamicCommand) -> SpaceWorld:
        """
        Register and returns the SubModule.

        Args:
            func(): SubModule

        Returns:
            The same SubModule
        """
        return SpaceWorld(func=func, version=version, **kwargs)

    return wrap

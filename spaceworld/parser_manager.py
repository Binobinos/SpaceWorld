import inspect
from typing import get_origin, List, Tuple, FrozenSet, Set, Unpack

from spaceworld import AnnotationManager, BaseModule
from spaceworld._types import (
    Kwargs,
    Args,
    Arg,
    Parameters,
    NewArgs,
    NewKwargs,
    CacheType,
    TupleArgs,
    UserAny,
    AnnotateArgType,
)
from spaceworld.utils import startswith_value, CommandCacheEntry


class ParserManager:
    def __init__(self, annotation_manager: AnnotationManager) -> None:
        self.am: AnnotationManager = annotation_manager

    @staticmethod
    def search_command(command: Args | TupleArgs, core) -> CommandCacheEntry:
        """
        Recursively searches for a command in the SpaceWorld command hierarchy.

        This internal method handles command lookup through:
        - Global command registry
        - Module-specific commands
        - Nested module structures
        - Argument separation

        Args:
            core ():
            command: Tokenized command parts (split by spaces)

        Returns:
            dict | bool:
                - Dictionary with keys:
                  * "command": Found BaseCommand instance
                  * "args": Remaining command arguments
                - False if command not found

        Behavior:
            1. Splits command into first argument and remaining parts
            2. Searches in this order:
               a) Global commands (if no module specified)
               b) Module commands
               c) Submodules (recursively)
            3. Returns immediately when first match is found

        Notes:
            - This is an internal method used by the command execution system
            - Handles both simple commands and module-qualified commands
            - Maintains separation between command and arguments
            - Uses depth-first search through module hierarchy
        """
        if not command:
            return {"command": None, "args": (), "module": None}
        first_arg, *args = command
        first_arg = first_arg.replace("-", "_")
        module: BaseModule | UserAny = core
        while [first_arg] + args:
            modules, commands = module.modules, module.commands
            _module: None | BaseModule = (
                None if isinstance(module, type(core)) else module
            )
            if first_arg in commands:
                return {"command": commands[first_arg], "args": args, "module": _module}
            if first_arg in modules:
                module = modules[first_arg]
                try:
                    first_arg, *args = args
                except ValueError:
                    break
            else:
                args = [first_arg.replace("_", "-")] + args
                return {"command": None, "args": args, "module": _module}
        return {"command": None, "args": (), "module": module}

    def pre_preparing_arg(
            self, args: TupleArgs, parameters: Parameters, default_flags: list[str]
    ) -> tuple[Args, Kwargs]:
        """
        Prepare arguments.

        into a tuple of named and positional arguments
        Args:
            default_flags ():
            parameters ():
            args(): A bare list of arguments

        Returns:
            tuple of named and positional arguments
        """
        errors = []
        positional_args: Args = []
        keyword_args: Kwargs = {}
        waiting_flag: str | None = None
        params: dict[str, inspect.Parameter] = {
            param.name: param for param in parameters
        }
        check_flag = True
        for arg in args:
            try:
                if not check_flag:
                    positional_args.append(arg)
                    continue
                if not arg.startswith("-"):
                    waiting_flag = self._set_positional_arg(
                        arg, positional_args, keyword_args, params, waiting_flag
                    )
                    continue
                if not arg.startswith("--"):
                    waiting_flag = self._preparing_short_flag(
                        arg,
                        positional_args,
                        keyword_args,
                        params,
                        default_flags,
                        waiting_flag,
                    )
                    continue
                if arg == "--":
                    check_flag = False
                    continue
                arg = arg[2:]
                if "=" in arg:
                    self._preparing_value_flag(arg, keyword_args, params)
                    waiting_flag = None
                    continue
                if waiting_flag:
                    flag = waiting_flag
                    waiting_flag = None
                    raise TypeError(
                        f"The pending flag '--{flag}' has not received a value before moving on to the next flag '--{arg}'."
                    )
                is_no: bool = arg.startswith("no-")
                name: str = arg[3:].replace("-", "_") if is_no else arg
                waiting_flag = self._preparing_bool_flag(
                    name, is_no, keyword_args, default_flags, params.get(name)
                )
            except Exception as error:
                errors.append(str(error))
                waiting_flag = None
        if waiting_flag:
            errors.append(f"The expected flag --{waiting_flag} didn't get a value.")
        if errors:
            raise ValueError(f"Errors in pre-preparing args:\n- {'\n- '.join(errors)}")
        return positional_args, keyword_args

    @staticmethod
    def set_kwargs_value(
            name: str, value: str | bool, kwargs: Kwargs, param: inspect.Parameter
    ):
        name = name.replace("-", "_")
        if name not in kwargs:
            kwargs[name] = value
        else:
            if param:
                if param.annotation is bool:
                    raise TypeError(f"The Boolean flag --{name} cannot be overwritten")
                origin = get_origin(param.annotation) or param.annotation
                if origin in {
                    list,
                    tuple,
                    set,
                    frozenset,
                    List,
                    Tuple,
                    Set,
                    FrozenSet,
                }:
                    if not isinstance(kwargs[name], list):
                        _value = kwargs[name]
                        kwargs[name] = []
                        kwargs[name].append(_value)
                    kwargs[name].append(value)
                else:
                    raise TypeError(
                        f"Redefining a non-iterable argument '{name}':'{kwargs[name]}' = {value}"
                    )
            else:
                if not isinstance(kwargs[name], list):
                    _value = kwargs[name]
                    kwargs[name] = []
                    kwargs[name].append(_value)
                kwargs[name].append(value)

    def _preparing_bool_flag(
            self,
            name: str,
            is_no: bool,
            keyword_args: Kwargs,
            default_flags: list[str],
            param: inspect.Parameter,
    ) -> str | None:
        """
        Handle bool flags.

        Args:
            keyword_args (): Dictionary of arguments

        Returns:
            None
        """
        waiting_flag = name
        if not name:
            raise ValueError("Invalid flag name: Empty name")
        if waiting_flag.lower() in default_flags or (
                param and param.annotation is not param.empty and param.annotation is bool
        ):
            waiting_flag = None
            self.set_kwargs_value(name, not is_no, keyword_args, param)
        return waiting_flag

    def _preparing_value_flag(
            self, arg: Arg, keyword_args: Kwargs, params: dict[str, inspect.Parameter]
    ) -> None:
        """
        Prepare flags with the value.

        Args:
            arg(): Argument
            keyword_args (): Dictionary of arguments

        Returns:
            None
        """
        name, _, value = arg.partition("=")
        if not name:
            raise ValueError("Invalid flag name: Empty name")
        name = name.replace("-", "_")
        vl = value.lower()
        condition = startswith_value(vl, '"') or startswith_value(vl, "'")
        value = value[1:-1] if condition else value
        vlue = (vl == "true") if vl in {"false", "true"} else value
        self.set_kwargs_value(name, vlue, keyword_args, params.get(name))

    def _set_positional_arg(
            self,
            arg: Arg,
            positional_args: Args,
            keyword_args: Kwargs,
            params: dict[str, inspect.Parameter],
            waiting_flag: bool,
    ) -> bool:
        if waiting_flag is not None:
            type_param = params.get(waiting_flag)
            if (
                    type_param
                    and type_param.annotation is not type_param.empty
                    and type_param.annotation is bool
            ):
                raise TypeError("The Boolean-flag may not matter")
            self.set_kwargs_value(waiting_flag, arg, keyword_args, type_param)
            waiting_flag = None
        else:
            positional_args.append(arg)
        return waiting_flag

    def _preparing_short_flag(
            self,
            arg: Arg,
            positional_args: Args,
            keyword_args: Kwargs,
            params: dict[str, inspect.Parameter],
            default_flags: list[str],
            waiting_flag: bool,
    ) -> bool:
        """
        Prepare a one-letter flag(-h, -abc, and the like).

        Args:
            arg(): single-letter argument
            keyword_args ():  Dictionary of arguments

        Returns:
            None
        """
        try:
            float(arg)
            waiting_flag = self._set_positional_arg(
                arg, positional_args, keyword_args, params, waiting_flag
            )
        except ValueError as e:
            arg = arg[1:]
            for num, name in enumerate(arg):
                name = name.lower()
                if name == "=" and num > 0:
                    self.set_kwargs_value(arg[num - 1], arg[:num], keyword_args, param)
                    waiting_flag = None
                    break
                if waiting_flag:
                    raise ValueError(
                        f"Incorrect syntax: {arg}"
                        "You cannot use short flags with a value in a chain of short flags. "
                        f"Use: {' '.join(f'-{name} value' for name in arg)}"
                    )
                waiting_flag = name
                param = params.get(name)
                if waiting_flag.lower() in default_flags or (
                        param
                        and param.annotation is not param.empty
                        and param.annotation is bool
                ):
                    waiting_flag = None
                    self.set_kwargs_value(name, True, keyword_args, param)
        return waiting_flag

    def preparing_args(
            self,
            parameters: Parameters,
            positional_args: Args | NewArgs,
            keyword_args: Kwargs | NewKwargs,
            system_flag: set[str],
    ) -> CacheType:
        """
        Process raw command arguments into properly typed and structured parameters.

        This internal method handles:
        - Argument parsing and validation
        - Type conversion using annotations
        - Positional vs keyword argument separation
        - Default value handling
        - Special flag processing (--no-*, -x, etc.)

        Args:
            system_flag ():
            positional_args ():
            keyword_args ():
            parameters: List of command parameter specifications from inspection

        Returns:
            tuple: Contains three elements:
                1. List of processed positional arguments
                2. Dictionary of processed keyword arguments
                3. Dictionary of raw flags (for special handling)

        Raises:
            ValueError: When argument value cannot be converted to expected type
            TypeError: When required arguments are missing

        Behavior:
            1. Separates positional args from flags (--prefix)
            2. Processes special flag formats:
               - --flag=value
               - --no-flag (sets False)
               - -xyz (sets x=True, y=True, z=True)
            3. Matches arguments to parameters using:
               - Parameter kind (POSITIONAL, KEYWORD, etc.)
               - Type annotations
               - Default values
            4. Performs type conversion when annotations are present
            5. Validates required parameters are provided


        Notes:
            - Uses inspect.Parameter information for validation
            - Supports variable arguments (*args, **kwargs)
            - Handles type conversion through registered annotations
            - Preserves original flag values for special handling
        """
        positional_args_index: int = 0
        new_args_positional: NewArgs = []
        new_args_keyword: NewKwargs = {}
        errors: dict[str, str] = {}
        for param in parameters:
            param_name = param.name
            try:
                match param.kind:
                    case param.VAR_POSITIONAL:
                        self._preparing_var_positional(
                            positional_args, new_args_positional, param
                        )
                        positional_args_index = len(positional_args)
                    case param.KEYWORD_ONLY if param_name in keyword_args:
                        value = keyword_args.pop(param_name)
                        new_args_keyword[param_name] = self._preparing_annotate(
                            param, value
                        )
                    case param.VAR_KEYWORD:
                        self._preparing_var_keyword(
                            keyword_args, new_args_keyword, param
                        )
                    case _ if param_name in keyword_args:
                        value = keyword_args.pop(param_name)
                        new_args_keyword[param_name] = self._preparing_annotate(
                            param, value
                        )
                    case _ if (
                            positional_args_index < len(positional_args)
                            and param.kind != param.KEYWORD_ONLY
                    ):
                        value = positional_args.pop(0)
                        new_args_positional.append(
                            self._preparing_annotate(param, value)
                        )

                    case _ if param.default != param.empty:
                        self._preparing_default(
                            new_args_positional, new_args_keyword, param
                        )
                    case _:
                        raise KeyError(
                            f"Missing required "
                            f"{
                            f'argument: {param_name}'
                            if param.kind
                               in {
                                   param.kind.POSITIONAL_ONLY,
                                   param.kind.POSITIONAL_OR_KEYWORD,
                               }
                            else f'flag: --{param_name}'
                            }"
                        )
            except Exception as error:
                errors[param_name] = str(error)
        if (
                errors
                or positional_args
                or (
                keyword_args
                and not (any(keyword_args.get(name) for name in system_flag))
        )
        ):
            msgs = [
                f"Errors in preparing args:\n-{'\n-'.join(f"'{name}': {error}" for name, error in sorted(errors.items()))} "
                if errors
                else "",
                f"Unnecessary positional arguments: '{', '.join(sorted(positional_args))}'"
                if positional_args
                else "",
                f"Unnecessary named arguments: '"
                f"{', '.join(sorted(f'--{name}' if len(name) > 1 else f'-{name}' for name in keyword_args))}'"
                if keyword_args
                else "",
            ]
            raise ValueError("\n".join(msg for msg in msgs if msg))
        return new_args_positional, new_args_keyword, keyword_args

    def _preparing_annotate(
            self, prm: inspect.Parameter, value: UserAny
    ) -> AnnotateArgType:
        """
        Perform annotation if the annotation is not empty.

        Args:
            prm (): annotation
            value (): Argument

        Returns:
            None
        """
        try:
            return (
                self.am.annotate(prm.annotation, value)
                if prm.annotation != prm.empty
                else value
            )
        except Exception as e:
            raise TypeError(f"Invalid argument for '{prm.name}': \n{e}") from e

    def _preparing_var_positional(
            self, new_args: Args, new_args_positional: NewArgs, prm: inspect.Parameter
    ) -> None:
        """
        Prepare *args arguments.

        Args:
            prm(): Parameter class
            new_args(): List of args arguments
            new_args_positional (): List of kwargs arguments

        Returns:
            None
        """
        if prm.annotation.__origin__ is Unpack:
            new_args_positional += [
                *self.am.annotate(prm.annotation.__args__[0], new_args)
            ]

        else:
            new_args_positional += (
                [self.am.annotate(prm.annotation, arg) for arg in new_args]
                if prm.annotation != prm.empty
                else new_args
            )
        new_args.clear()

    def _preparing_var_keyword(
            self, lst: Kwargs, new_args_keyword: NewKwargs, prm: inspect.Parameter
    ) -> None:
        """
        Prepare **kwargs arguments.

        Args:
            lst (): Kwargs
            new_args_keyword (): List of kwargs arguments
            prm (): Parameter class

        Returns:
            None
        """
        annotate = self._preparing_annotate
        if prm.annotation.__origin__ is Unpack:
            value = self.am.annotate(prm.annotation.__args__[0], lst)
            if not isinstance(value, dict):
                raise ValueError("Unpack annotation must be dict")
            new_args_keyword.update(value)
            lst.clear()
            return
        for name, value in lst.items():
            new_args_keyword[name] = annotate(prm, value)

    def _preparing_default(
            self,
            new_args_positional: NewArgs,
            new_args_keyword: NewKwargs,
            prm: inspect.Parameter,
    ) -> None:
        """
        Prepare default values.

        Args:
            new_args_keyword (): List of arguments to kwargs
            new_args_positional (): List of args arguments
            prm(): Parameter class

        Returns:
            None
        """
        value = prm.default
        if prm.kind in {
            prm.KEYWORD_ONLY,
            prm.VAR_KEYWORD,
            prm.POSITIONAL_OR_KEYWORD,
        }:
            new_args_keyword[prm.name] = self._preparing_annotate(prm, value)
            return
        new_args_positional.append(self._preparing_annotate(prm, value))

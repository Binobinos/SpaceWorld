"""Implementing the basic SpaceWorld command."""

from inspect import Parameter

from ._types import (
    Args,
    UserAny,
)
from .command import Command


class BaseCommand(Command):
    """
    Base class for SpaceWorld command implementations.

    Encapsulates command behavior and metadata including:
    - Command execution (sync/async)
    - Help documentation generation
    - Parameter inspection
    - Activation modes
    - Deprecation status
    - Confirmation requirements

    Attributes:
        name: Primary command name
        aliases: Alternative command names
        func: Callable implementation
    """

    __slots__ = ()

    def get_msg(self) -> tuple[str, str]:
        """
        Возвращает кортеж сообщений.

        Returns:
            Сообщение об устаревшей команде и confirm команде
        """
        deprecated_msg = (
            f"Deprecated: {'YES' if isinstance(dp, bool) else f'the message: {dp}'}"
            if (dp := self.config["deprecated"])
            else ""
        )
        confirmation_msg = (
            f"Confirm {'ation YES' if isinstance(cm, bool) else f'ing the message: {cm}'} "
            if (cm := self.config["confirm"])
            else ""
        )
        return deprecated_msg, confirmation_msg

    def get_help_doc(self) -> str:
        """
        Generate formatted help documentation for the command.

        Returns:
            str: Multi-line help text containing:
                 - Name and aliases
                 - Documentation
                 - Usage example
                 - Activation modes
                 - Parameter details
                 - Visibility status
                 - Deprecation status
                 - Confirmation requirements
        """
        deprecated_msg, confirmation_msg = self.get_msg()
        args = self._get_args_info()
        return (
            f"Usage: {self.examples}"
            f"{self.big_docs or 'None documentation'}\n"
            f"{f'Args: \n{args}\n\n' if args else ''}\n"
            f"Options: \n{self._get_options_info()}\n"
            f"{'Hidden' if self.config['hidden'] else ''}\n"
            f"{deprecated_msg}"
            f"{confirmation_msg}"
        )

    def generate_example(self, examples: str | Args) -> str:
        """
        Generate documentation for the team.

        Args:
            examples (): One example or a list of examples
        Returns:
            example table
        """
        prefix: dict[UserAny, str] = {
            Parameter.KEYWORD_ONLY: "--",
            Parameter.VAR_POSITIONAL: "*",
            Parameter.VAR_KEYWORD: "**",
        }

        msg = " ".join(
            [
                (
                    "["
                    f"{prefix.get(prm.kind, '')}"
                    f"{prm.name}: {an.__name__ if (an := prm.annotation) != prm.empty else 'Any'}"
                    f"{f" = '{prm.default}'" if prm.default != prm.empty else ''}"
                    "]"
                )
                for prm in self.parameters
            ]
        )
        examples = "\n".join(examples) if isinstance(examples, list) else examples
        return f"{self.name} [ARGS] [OPTIONS] {msg} \n{examples}"

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
                f"  {prm.name}: {prm.annotation}"
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
        system_options = [
            "  --help - Displays the help on the command",
            "  --force - Disables command confirmations(For confirm command)"
            if self.config["confirm"]
            else "",
        ]
        options = [
                      f"  --{prm.name.replace('_', '-')}: {prm.annotation.__name__} = {prm.default}"
                      for prm in self.parameters
                      if prm.kind in {prm.KEYWORD_ONLY, prm.VAR_KEYWORD} or prm.annotation is bool
                  ] + system_options
        return "\n".join(options)

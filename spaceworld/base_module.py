"""Implementation of the Module's Base Class in SpaceWorld."""

from .module import Module


class BaseModule(Module):
    """
    Base class for creating command modules in SpaceWorld.

    Modules act as containers for related commands and submodules, providing:
    - Command registration and organization
    - Hierarchical command structures via submodules
    - Command metadata and configuration
    - Documentation support

    Attributes:
        name: Module identifier
        docs: Module description
        commands: Dictionary of registered commands
        modules: Dictionary of nested submodules
    """

    __slots__ = ()

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
        examples = "\n\t".join(
            f"{cmd.examples}\t{cmd.config['docs']}" for cmd in self.commands.values()
        )
        msg = f"\n\t{examples}"
        return (
            f"Module `{self.name}` {f'- {self.docs.strip()}' if self.docs.strip() else ''}\n"
            f"Commands: {msg}\n"
            "Module Flags: \n"
            "\n\t--help\\-h \tDisplays the help\n"
            "\n\t--force\\-f\tCancels confirmation\n"
            "For reference on a specific command: \n"
            f"\t{self.name} <command> --help/-h\n"
        )

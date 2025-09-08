"""
The basic Abstract Writer class for console output.

Inherit your class from it to create a unique output.
"""

from abc import ABC, abstractmethod

from ._types import UserAny


class Writer(ABC):
    """Abstract base class defining a console output writer interface with styled messaging."""

    __slots__ = ()

    @abstractmethod
    def write(self, *text: UserAny, prefix: str = "") -> None:
        """
        Write text to console with optional styling (colors/fonts).

        Args:
            prefix ():
            *text: Content to display (accepts multiple arguments)

        Note:
            Implementing classes should handle basic string conversion of non-string types.
        """

    @abstractmethod
    def info(self, *text: UserAny) -> None:
        """
        Display informational message to console.

        Args:
            *text: Information content (multiple arguments will be concatenated)

        Note:
            Typically displayed in neutral/style color (e.g., blue or default terminal color).
        """

    @abstractmethod
    def warning(self, *text: UserAny) -> None:
        """
        Output a warning message to console.

        Args:
            *text: Warning content (accepts multiple arguments)

        Note:
            Should be visually distinct from regular messages (e.g., yellow color).
        """

    @abstractmethod
    def input(self, *text: UserAny) -> None:
        """
        Display input prompt or input state information.

        Args:
            *text: Prompt or input-related information

        Note:
            Used when soliciting user input or showing input context.
        """

    @abstractmethod
    def error(self, *text: UserAny) -> None:
        """
        Output an error message to console.

        Args:
            *text: Error content (accepts multiple arguments)

        Note:
            Should be highly visible (typically red color) and distinguishable from warnings.
        """

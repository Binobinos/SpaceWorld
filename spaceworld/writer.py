"""
The basic Abstract Writer class for console output.

Inherit your class from it to create a unique output.
"""

from ._types import UserAny


class Writer:
    """Abstract base class defining a console output writer interface with styled messaging."""

    __slots__ = ()

    @staticmethod
    def write(
            *text: UserAny, prefix: str = "", sep: str = " ", end: str = "\n"
    ) -> None:
        """
        Output raw text to console without formatting.

        Args:
            end ():
            sep ():
            prefix ():
            *text: Items to display (will be space-joined and string-converted)
        """
        print(f"{prefix}{sep.join(str(item) for item in text)}", end=end)

    def info(self, *text: UserAny) -> None:
        """
        Display informational messages prefixed with 'INFO:'.

        Args:
            *text: Information content items
        """
        self.write(*text, prefix="INFO:")

    def warning(self, *text: UserAny) -> None:
        """
        Display warning messages prefixed with 'WARNING:'.

        Args:
            *text: Warning content items
        """
        self.write(*text, prefix="WARNING:")

    def error(self, *text: UserAny) -> None:
        """
        Display error messages prefixed with 'ERROR:'.

        Args:
            *text: Error content items
        """
        self.write(*text, prefix="ERROR:")

    def input(self, *text: UserAny) -> None:
        """
        Display input-related messages prefixed with 'INPUT:'.

        Args:
            *text: Input context items
        """
        self.write(*text, prefix="INPUT:")

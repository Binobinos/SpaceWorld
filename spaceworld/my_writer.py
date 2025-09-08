"""The implementation of the MyWriter class is inherited from Writer. Uses print."""

from ._types import UserAny

from .writer import Writer


class MyWriter(Writer):
    """
    Basic console writer implementation that formats messages with prefixes.

    This concrete writer implements the Writer interface by:
    - Adding message type prefixes (INFO/WARNING/ERROR/INPUT)
    - Joining multiple text arguments with spaces
    - Outputting to standard print()

    Suitable for basic console applications where simple formatted output is needed.
    """

    __slots__ = ()

    def write(self, *text: UserAny, prefix: str = "") -> None:
        """
        Output raw text to console without formatting.

        Args:
            prefix ():
            *text: Items to display (will be space-joined and string-converted)
        """
        print(f"{prefix}{' '.join(str(item) for item in text)}")

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

"""Command Exception File."""

from .spaceworld_error import SpaceWorldError


class CommandError(SpaceWorldError):
    """
    Base exception for command processing failures.

    Covers errors related to:
    - Command execution
    - Command validation
    - Command lifecycle management
    """


class CommandCreateError(CommandError):
    """
    Exception raised during command registration failures.

    Specific cases include:
    - Duplicate command names
    - Invalid command configurations
    - Command initialization errors
    """

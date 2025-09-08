"""SpaceWorld Base Exclusion file."""


class SpaceWorldError(Exception):
    """
    Base exception class for all SpaceWorld-related errors.

    This serves as the root exception for the SpaceWorld system,
    allowing catching all framework-specific errors with a single exception class.
    """


class ExitError(SpaceWorldError):
    """It is a designation for getting out of the context of the handler method."""

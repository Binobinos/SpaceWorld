"""SpaceWorld errors."""


class SpaceWorldError(Exception):
    """
    Base exception class for all SpaceWorld-related errors.

    This serves as the root exception for the SpaceWorld system,
    allowing catching all framework-specific errors with a single exception class.
    """


class ExitError(SpaceWorldError):
    """It is a designation for getting out of the context of the handler method."""


class AnnotationsError(SpaceWorldError):
    """
    Exception raised for annotation-related failures.

    Typical cases include:
    - Duplicate annotation registration
    - Invalid annotation types
    - Annotation processing failures
    """


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


class ModuleError(SpaceWorldError):
    """
    Base exception for module-related operations.

    Encompasses errors occurring during:
    - Module loading
    - Module initialization
    - Module dependency resolution
    """


class ModuleCreateError(ModuleError):
    """
    Exception raised during module instantiation failures.

    Common scenarios:
    - Duplicate module names
    - Invalid module configurations
    - Circular dependencies
    """


class SubModuleCreateError(ModuleCreateError):
    """
    Exception specific to submodule registration failures.

    Specialized cases include:
    - Invalid submodule hierarchies
    - Namespace collisions in nested modules
    - Parent-child module relationship violations
    """

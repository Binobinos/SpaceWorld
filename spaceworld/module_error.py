"""The Module's Exception File."""

from .spaceworld_error import SpaceWorldError


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

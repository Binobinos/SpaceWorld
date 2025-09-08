"""Annotation Exclusion File."""

from .spaceworld_error import SpaceWorldError


class AnnotationsError(SpaceWorldError):
    """
    Exception raised for annotation-related failures.

    Typical cases include:
    - Duplicate annotation registration
    - Invalid annotation types
    - Annotation processing failures
    """

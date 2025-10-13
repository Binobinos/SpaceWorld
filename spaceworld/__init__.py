"""
Spaceworld CLI is a new generation Cli framework.

for convenient development of your teams written in Python 3.12+
with support for asynchronous commands
"""

from .annotation_manager import AnnotationManager
from .base_command import BaseCommand
from .base_module import BaseModule
from .errors import (
    AnnotationsError,
    ModuleError,
    CommandError,
    SpaceWorldError,
    CommandCreateError,
    SubModuleCreateError,
    ModuleCreateError,
    ExitError,
)
from .parser_manager import ParserManager
from .spaceworld import SpaceWorld, run, spaceworld
from .utils import annotation_depends
from .writer import Writer
from .writer import Writer

__all__ = (
    "AnnotationManager",
    "AnnotationsError",
    "SpaceWorld",
    "BaseModule",
    "BaseCommand",
    "run",
    "Writer",
    "ModuleError",
    "ModuleCreateError",
    "CommandError",
    "ParserManager",
    "SpaceWorldError",
    "ExitError",
    "CommandCreateError",
    "SubModuleCreateError",
    "annotation_depends",
    "spaceworld",
)

__author__ = "binobinos"

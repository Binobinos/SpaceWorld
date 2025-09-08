"""
Spaceworld CLI is a new generation Cli framework.

for convenient development of your teams written in Python 3.12+
with support for asynchronous commands
"""

from .annotation_manager import AnnotationManager
from .annotations_error import AnnotationsError
from .base_command import BaseCommand
from .base_module import BaseModule
from .command_error import CommandError, CommandCreateError
from .module_error import ModuleError, ModuleCreateError, SubModuleCreateError
from .my_writer import MyWriter
from .spaceworld_cli import SpaceWorld, run, spaceworld
from .spaceworld_error import SpaceWorldError
from .util import annotation_depends
from .writer import Writer

__all__ = (
    "AnnotationManager",
    "AnnotationsError",
    "SpaceWorld",
    "BaseModule",
    "BaseCommand",
    "run",
    "MyWriter",
    "Writer",
    "ModuleError",
    "ModuleCreateError",
    "CommandError",
    "SpaceWorldError",
    "CommandCreateError",
    "SubModuleCreateError",
    "annotation_depends",
    "spaceworld",
)

__author__ = "binobinos"

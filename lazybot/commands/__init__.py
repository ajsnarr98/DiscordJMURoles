# -*- coding: utf-8 -*-

"""
lazybot.commands
~~~~~~~~~~~~~~~~~~~~~
A module holding commands and auto-response functions
for a discord bot.
"""

import inspect
import os
import sys
import types

from importlib.machinery import SourceFileLoader
from typing import List

from discord.ext.commands import Cog

_COMMANDS: List[Cog] = []


def all_commands() -> List[Cog]:
    """
    Provide a copy of the list of commands.
    """
    return list(_COMMANDS)


def load_commands():
    """
    Loads the commands that are contained within this package.
    """

    directory = os.path.dirname(os.path.realpath(__file__))

    modules = list(
        {
            command_file
            for command_file in os.listdir(directory)
            if command_file.endswith(".py") and command_file != "__init__.py"
        }
    )

    for module in modules:
        path = os.path.join(directory, module)
        modname = os.path.splitext(os.path.basename(path))[0]

        try:
            loader = SourceFileLoader(f"{__name__}.{modname}", path)
            command_module = types.ModuleType(loader.name)
            loader.exec_module(command_module)
        except (ImportError, SyntaxError) as import_error:
            print(
                f"Unable to load command from {module}: {import_error}", file=sys.stderr
            )
        else:
            # Load all the contents of the modules and check if they are
            # subclasses of Cog. IF they are, add them to the commands list.
            module_contents = [
                getattr(command_module, content_name)
                for content_name in dir(command_module)
            ]
            _COMMANDS.extend(
                {
                    command_class
                    for command_class in module_contents
                    if _is_loaded_subclass(command_class, Cog)
                }
            )


def _is_loaded_subclass(test_class: type, parent: type) -> bool:
    """
    Checks whether the given class is a subclass of the given parent class
    and determines whether it looks like the class was loaded through
    load_resources, rather than having been imported the normal way.

    :param test_class: The class to test as a subclass
    :param parent: The class to test as the parent class
    :returns: Whether the test_class is a subclass of parent
    :rtype: bool
    """

    return (
        (inspect.isclass(test_class))
        and (inspect.getmodule(test_class) is None)
        and issubclass(test_class, parent)
    )


# Load the commands, but only if that hasn't already been done.
if not _COMMANDS:
    load_commands()

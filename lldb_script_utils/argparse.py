#!/usr/bin/env python
"""Arguments parser tailored to LLDB style of command line parsing."""

import shlex
import sys
from abc import abstractmethod, ABC
from argparse import ArgumentParser, ArgumentError
from gettext import gettext as _
from typing import Optional, Tuple, Type, Callable, Any

import lldb

from lldb_script_utils.core import LLDBCommand

DEFAULT_SUBCOMMANDS_TITLE = _('The following subcommands are supported')
DEFAULT_SUBCOMMANDS_METAVAR = _('<subcommand>')


def _format_subcommands_epilog(subcommands_metavar: str) -> str:
    return _("For more help on any particular subcommand, type '{}'.").format(
        f'%(prog)s {subcommands_metavar} --help')


def _capitalize_args_parser_strings(args_parser: ArgumentParser):
    """Capitalize certain strings in ArgumentParser.

    ArgumentParser provides human-readable strings, each starting with a
    lowercase letter.  We capitalize those strings for consistency.
    """
    if not hasattr(args_parser, '_action_groups'):
        return
    # pylint: disable=protected-access
    # noinspection PyProtectedMember
    for action_group in args_parser._action_groups:
        action_group.title = action_group.title.capitalize()
        # noinspection PyProtectedMember
        for action in action_group._actions:
            if action.dest == 'help':
                action.help = _('Show this help message and exit.')
                break


class LLDBArgumentParser(ArgumentParser):
    """An ArgumentParser that mimics the LLDB style of command line parsing.

    Normally returned from `LLDBArgumentParser.Command.create_args_parser()`.
    """
    class Command(LLDBCommand):
        """Command protocol.

        A conforming subclass should provide `create_args_parser`.
        """
        def __init__(self, debugger: lldb.SBDebugger, bindings: dict):
            """Creates an argument parser for this command object."""
            super().__init__(debugger, bindings)
            self.args_parser = self.create_args_parser(debugger=debugger,
                                                       bindings=bindings)

        def __call__(self, debugger: lldb.SBDebugger, command: str,
                     execution_context: lldb.SBExecutionContext,
                     command_return: lldb.SBCommandReturnObject) -> None:
            """Parses a command string, and runs a command handler."""
            try:
                args = self.args_parser.parse_args(shlex.split(command))
            except ArgumentError as err:
                command_return.SetError(str(err))
                return
            if not hasattr(args, 'command_handler'):
                self.args_parser.print_usage(file=sys.stderr)
                return
            args.command_handler(debugger=debugger,
                                 execution_context=execution_context,
                                 command_return=command_return,
                                 **vars(args))

        def get_short_help(self) -> str:
            return self.args_parser.lldb_short_help

        def get_long_help(self) -> str:
            return self.args_parser.lldb_long_help

        @abstractmethod
        def create_args_parser(self, debugger: lldb.SBDebugger,
                               bindings: dict) -> 'LLDBArgumentParser':
            pass

    class Subcommand(ABC):
        """Subcommand protocol.

        A conforming subclass should provide `create_args_subparser`.
        """
        @classmethod
        @abstractmethod
        def create_args_subparser(
                cls, add_subparser: Type[ArgumentParser]) -> ArgumentParser:
            pass

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            prog: str,
            help: str = '',  # pylint: disable=redefined-builtin
            add_help: bool = False,  # A default for a non-subcommand.
            **kwargs):
        """Initialize an argument parser."""
        self.lldb_short_help = help

        # Initialize ArgumentParser properties.
        super().__init__(prog=prog, add_help=add_help, **kwargs)
        _capitalize_args_parser_strings(self)

    def set_command_handler(self, command_handler: Callable) -> None:
        """Set a command handler function.

        Command handler receives the following arguments:

        - debugger: lldb.SBDebugger
        - execution_context: lldb.SBExecutionContext
        - command_return: lldb.SBCommandReturnObject
        - all arguments and options added to the argument parser.
        """
        self.set_defaults(command_handler=command_handler)

    def add_subcommands(self,
                        *args: Tuple[Type['LLDBArgumentParser.Subcommand'],
                                     Callable],
                        title=DEFAULT_SUBCOMMANDS_TITLE,
                        metavar=DEFAULT_SUBCOMMANDS_METAVAR) -> None:
        """Add one or more subcommands to a main command.

        Each subcommand is defined by a tuple of a Subcommand subclass and a
        subcommand handler.

        Subcommand subclass is responsible for creating and customizing a
        subparser for a subcommand.

        Subcommand handler is a function that receives the following arguments:

        - debugger: lldb.SBDebugger
        - execution_context: lldb.SBExecutionContext
        - command_return: lldb.SBCommandReturnObject
        - all arguments and options added to the main argument parser.
        - all arguments and options added to the subcommand argument parser.
        """

        # Provide a default LLDB-style epilog in case we have any subcommands.
        if self.epilog is None:
            self.epilog = _format_subcommands_epilog(metavar)

        # Create an action to which subcommands' subparsers will be added.
        subparsers_action = self.add_subparsers(title=title, metavar=metavar)

        # An internal factory function to be passed to a Subcommand subclass.
        # noinspection PyShadowingBuiltins
        def add_subparser(
                name: str,
                help: str,  # pylint: disable=redefined-builtin
                description: Optional[str] = None,
                add_help=True,  # A default for subcommand
                **kwargs: Any) -> ArgumentParser:
            # A `help` string is displayed in the list of subcommands displayed
            # in a main command help text.  If `help` string is not provided,
            # the whole subcommand will be suppressed from the list of
            # subcommands formatted by a main command parser.
            assert help
            # A `description` is displayed within a subcommand's help text.
            if description is None:
                description = help
            return subparsers_action.add_parser(name,
                                                help=help,
                                                description=description,
                                                add_help=add_help,
                                                **kwargs)

        # Iterate over tuples, make a subcommand class create a subparser.
        cls: Type[LLDBArgumentParser.Subcommand]
        for (cls, func) in args:
            # noinspection PyTypeChecker
            subparser = cls.create_args_subparser(add_subparser)
            subparser.set_defaults(command_handler=func)

    @property
    def lldb_long_help(self) -> str:
        # Add a single whitespace to align 'usage:' with the 'Syntax:' on the
        # previous line, as displayed by the LLDB `help` command.
        return ' ' + self.format_help()

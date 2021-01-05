"""An example of a test command with subcommands."""

import lldb
from argparse import ArgumentParser
from typing import Type
from lldb_script_utils.argparse import LLDBArgumentParser
from lldb_script_utils.debugger_utils import format_command_script_add


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    TestCommand2.lldb_init_class(debugger)


class TestCommand2(LLDBArgumentParser.Command):
    """A test command with subcommands."""
    NAME = 'testCommand2'
    HELP = 'Help on testCommand2.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger.HandleCommand(format_command_script_add(cls.NAME, cls))

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> ArgumentParser:
        parser = LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_subcommands(
            (self.Subcommand1, self._on_subcommand1),
            (self.Subcommand2, self._on_subcommand2),
        )
        return parser

    class Subcommand1(LLDBArgumentParser.Subcommand):
        """The first subcommand."""
        NAME = 'subcommand1'
        HELP = 'Help on subcommand1.'

        @classmethod
        def create_args_subparser(
                cls, add_subparser: Type[ArgumentParser]) -> ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    def _on_subcommand1(self, **_):
        print('Hello from subcommand1')

    class Subcommand2(LLDBArgumentParser.Subcommand):
        """The second subcommand."""
        NAME = 'subcommand2'
        HELP = 'Help on subcommand2.'

        @classmethod
        def create_args_subparser(
                cls, add_subparser: Type[ArgumentParser]) -> ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    def _on_subcommand2(self, **_):
        print('Hello from subcommand2')

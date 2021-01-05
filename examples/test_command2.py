"""An example of a test command with subcommands."""

import lldb
import argparse
from typing import Type
from lldb_script_utils import lldb_commands
from lldb_script_utils import debugger_utils


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    TestCommand2.lldb_init_class(debugger)


class TestCommand2(lldb_commands.LLDBCommand):
    """A test command with subcommands."""
    NAME = 'testCommand2'
    HELP = 'Help on testCommand2.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger_utils.handle_command_script_add(debugger, cls.NAME, cls)

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> lldb_commands.LLDBArgumentParser:
        parser = lldb_commands.LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_subcommands(
            (self.Subcommand1, self._on_subcommand1),
            (self.Subcommand2, self._on_subcommand2),
        )
        return parser

    class Subcommand1(lldb_commands.LLDBSubcommand):
        """The first subcommand."""
        NAME = 'subcommand1'
        HELP = 'Help on subcommand1.'

        @classmethod
        def create_args_subparser(
            cls, add_subparser: Type[argparse.ArgumentParser]
        ) -> argparse.ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    def _on_subcommand1(self, **_):
        print('Hello from subcommand1')

    class Subcommand2(lldb_commands.LLDBSubcommand):
        """The second subcommand."""
        NAME = 'subcommand2'
        HELP = 'Help on subcommand2.'

        @classmethod
        def create_args_subparser(
            cls, add_subparser: Type[argparse.ArgumentParser]
        ) -> argparse.ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            return subparser

    def _on_subcommand2(self, **_):
        print('Hello from subcommand2')

"""An example of a test command with an argument."""

import lldb
from argparse import ArgumentParser
from lldb_script_utils.argparse import LLDBArgumentParser
from lldb_script_utils.core import format_command_script_add


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    TestCommand1.lldb_init_class(debugger)


class TestCommand1(LLDBArgumentParser.Command):
    """A test command with an argument."""
    NAME = 'testCommand1'
    HELP = 'Help on testCommand1.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger.HandleCommand(format_command_script_add(cls.NAME, cls))

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> ArgumentParser:
        parser = LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_argument('magic_number',
                            type=int,
                            help='An answer to the question.')
        parser.set_command_handler(self._on_command1)
        return parser

    def _on_command1(self, magic_number: int, **_):
        print(f'The answer is {magic_number}')

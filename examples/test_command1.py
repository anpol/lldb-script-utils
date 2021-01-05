"""An example of a test command with an argument."""

import lldb

from lldb_script_utils import debugger_utils
from lldb_script_utils import lldb_commands


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    TestCommand1.lldb_init_class(debugger)


class TestCommand1(lldb_commands.LLDBCommand):
    """A test command with an argument."""
    NAME = 'testCommand1'
    HELP = 'Help on testCommand1.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger_utils.handle_command_script_add(debugger, cls.NAME, cls)

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> lldb_commands.LLDBArgumentParser:
        parser = lldb_commands.LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_argument('magic_number', type=int, help='Help on magic.')
        parser.set_command_handler(self._on_command1)
        return parser

    def _on_command1(self, magic_number: int, **_):
        print(f'The answer is {magic_number}')

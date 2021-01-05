#!/usr/bin/env python
"""Tests for LLDB-style argument parser."""

import io
import unittest
from argparse import ArgumentParser
from typing import Type

import lldb

from lldb_script_utils.argparse import LLDBArgumentParser
from lldb_script_utils.debugger_utils import format_command_script_add

TEST_PACKAGE = f'{__package__}.argparse_test'


def _create_debugger_for_testing() -> lldb.SBDebugger:
    debugger = lldb.SBDebugger.Create()
    debugger.SetOutputFile(io.StringIO())  # Ignore output
    debugger.HandleCommand(f'command script import {TEST_PACKAGE}')
    return debugger


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
    # pylint: disable=invalid-name
    TestCommand1.lldb_init_class(debugger)
    TestCommand2.lldb_init_class(debugger)


class TestCommand1(LLDBArgumentParser.Command):
    """A test command with an argument and an option."""
    NAME = 'testCommand1'
    HELP = 'Help on testCommand1.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger.HandleCommand(format_command_script_add(cls.NAME, cls))

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> ArgumentParser:
        parser = LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_argument('magic_number', type=int)
        parser.add_argument('--good-option', action='store_true')
        parser.set_command_handler(self._on_command1)
        return parser

    def _on_command1(self, magic_number: int, good_option: bool, **_):
        print(f'Hello from {self.NAME} ' +
              f'magic_number={magic_number} good_option={good_option}')


class TestCommand2(LLDBArgumentParser.Command):
    """A test command with a global option and two subcommands."""
    NAME = 'testCommand2'
    HELP = 'Help on testCommand2.'

    @classmethod
    def lldb_init_class(cls, debugger: lldb.SBDebugger) -> None:
        debugger.HandleCommand(format_command_script_add(cls.NAME, cls))

    def create_args_parser(self, debugger: lldb.SBDebugger,
                           bindings: dict) -> ArgumentParser:
        parser = LLDBArgumentParser(self.NAME, self.HELP)
        parser.add_argument('--global-option', action='store_true')
        parser.add_subcommands(
            (self.Subcommand1, self._on_subcommand1),
            (self.Subcommand2, self._on_subcommand2),
        )
        return parser

    class Subcommand1(LLDBArgumentParser.Subcommand):
        """A subcommand with an option."""
        NAME = 'subcommand1'
        HELP = 'Help on subcommand1.'

        @classmethod
        def create_args_subparser(
                cls, add_subparser: Type[ArgumentParser]) -> ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            subparser.add_argument('--option1',
                                   action='store_true',
                                   help='Help on option1.')
            return subparser

    def _on_subcommand1(self, global_option: bool, option1: bool, **_):
        print(f'Hello from {self.NAME} {self.Subcommand1.NAME} ' +
              f'global_option={global_option} option1={option1}')

    class Subcommand2(LLDBArgumentParser.Subcommand):
        """A subcommand with an option."""
        NAME = 'subcommand2'
        HELP = 'Help on subcommand2.'

        @classmethod
        def create_args_subparser(
                cls, add_subparser: Type[ArgumentParser]) -> ArgumentParser:
            subparser = add_subparser(cls.NAME, cls.HELP)
            subparser.add_argument('--option2',
                                   action='store_true',
                                   help='Help on option2.')
            return subparser

    def _on_subcommand2(self, global_option: bool, option2: bool, **_):
        print(f'Hello from {self.NAME} {self.Subcommand2.NAME} ' +
              f'global_option={global_option} option2={option2}')


class LLDBArgumentParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.debugger = _create_debugger_for_testing()
        self.output_file = io.StringIO()
        self.debugger.SetOutputFile(self.output_file)
        self.error_file = io.StringIO()
        self.debugger.SetErrorFile(self.error_file)

    @property
    def combined_output(self):
        result = []

        def append_prefixed_value(prefix, value: str):
            nonlocal result
            if value:
                result += [prefix, value]

        append_prefixed_value('stdout:', self.output_file.getvalue())
        append_prefixed_value('stderr:', self.error_file.getvalue())
        return '\n'.join(result)

    def test_command1_help(self):
        self.debugger.HandleCommand(f'help {TestCommand1.NAME}')
        self.assertEqual(
            '''stdout:
     Help on testCommand1.  Expects 'raw' input (see 'help raw-input'.)

Syntax: testCommand1
 usage: testCommand1 [--good-option] magic_number

Positional arguments:
  magic_number

Optional arguments:
  --good-option
''', self.combined_output)

    def test_command1(self):
        TestCommand1.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand1.NAME} 42')
        self.assertEqual(
            '''stdout:
Hello from testCommand1 magic_number=42 good_option=False
''', self.combined_output)

    def test_command1_good_option(self):
        TestCommand1.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand1.NAME} --good-option 43')
        self.assertEqual(
            '''stdout:
Hello from testCommand1 magic_number=43 good_option=True
''', self.combined_output)

    def test_command1_bad_option(self):
        TestCommand1.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand1.NAME} --bad-option 44')
        self.assertEqual(
            '''stderr:
usage: testCommand1 [--good-option] magic_number
testCommand1: error: unrecognized arguments: --bad-option
''', self.combined_output)

    def test_command1_bad_argument(self):
        TestCommand1.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand1.NAME} NaN')
        self.assertEqual(
            '''stderr:
usage: testCommand1 [--good-option] magic_number
testCommand1: error: argument magic_number: invalid int value: 'NaN'
''', self.combined_output)

    def test_command2_help(self):
        self.debugger.HandleCommand(f'help {TestCommand2.NAME}')
        self.assertEqual(
            '''stdout:
     Help on testCommand2.  Expects 'raw' input (see 'help raw-input'.)

Syntax: testCommand2
 usage: testCommand2 [--global-option] <subcommand> ...

Optional arguments:
  --global-option

The following subcommands are supported:
  <subcommand>
    subcommand1    Help on subcommand1.
    subcommand2    Help on subcommand2.

For more help on any particular subcommand, type 'testCommand2 <subcommand>
--help'.
''', self.combined_output)

    def test_command2_subcommand1_help(self):
        self.debugger.HandleCommand(f'{TestCommand2.NAME} subcommand1 --help')
        self.assertEqual(
            '''stdout:
usage: testCommand2 subcommand1 [-h] [--option1]

Help on subcommand1.

Optional arguments:
  -h, --help  Show this help message and exit.
  --option1   Help on option1.
''', self.combined_output)

    def test_command2_good_option(self):
        TestCommand2.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(
            f'{TestCommand2.NAME} --global-option subcommand1 --option1')
        self.assertEqual(
            '''stdout:
Hello from testCommand2 subcommand1 global_option=True option1=True
''', self.combined_output)

    def test_command2_bad_option(self):
        TestCommand2.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(
            f'{TestCommand2.NAME} --bad-option subcommand1 --option1')
        self.assertEqual(
            '''stderr:
usage: testCommand2 [--global-option] <subcommand> ...
testCommand2: error: unrecognized arguments: --bad-option
''', self.combined_output)

    def test_command2_good_subcommand(self):
        TestCommand2.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand2.NAME} subcommand2')
        self.assertEqual(
            '''stdout:
Hello from testCommand2 subcommand2 global_option=False option2=False
''', self.combined_output)

    def test_command2_bad_subcommand(self):
        TestCommand2.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand2.NAME} badSubCommand')
        self.assertEqual(
            '''stderr:
usage: testCommand2 [--global-option] <subcommand> ...
testCommand2: error: argument <subcommand>: invalid choice: 'badSubCommand' \
(choose from 'subcommand1', 'subcommand2')
''', self.combined_output)

    def test_command2_no_subcommand(self):
        TestCommand2.lldb_init_class(self.debugger)
        self.debugger.HandleCommand(f'{TestCommand2.NAME}')
        self.assertEqual(
            '''stderr:
usage: testCommand2 [--global-option] <subcommand> ...
''', self.combined_output)


if __name__ == '__main__':
    unittest.main()

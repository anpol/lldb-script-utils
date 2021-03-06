<!-- vim:spell -->

# lldb-script-utils

This Python package provides functions and classes to support implementations
of custom LLDB commands.

The command line parsing, as well as the help text for your command are
provided automatically, thanks to
[argparse](https://docs.python.org/3/library/argparse.html) module.

## Installation

This repository is meant to be a submodule of
[lldb-bundle](//github.com/anpol/lldb-bundle), look there for installation instructions.

You also have an option to clone this repository and add the following line
into your `~/.lldbinit` file:
```
command script import <path-to-repository>/lldb_script_utils
```

## Quick Start

To create an LLDB command with this package, you need to subclass the
`LLDBArgumentParser.Command` and implement its `create_args_parser` method:

```python
import lldb

from lldb_script_utils import debugger_utils
from lldb_script_utils import lldb_commands


def __lldb_init_module(debugger: lldb.SBDebugger, _: dict) -> None:
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
```

The example above also demonstrates how to register your command with LLDB.

Assuming the file is saved as
[examples/test_command1.py](examples/test_command1.py), you can import it into
LLDB, and run:
```lldb
$ lldb

(lldb) command script import examples/test_command1.py

(lldb) help testCommand1
     Help on testCommand1.  Expects 'raw' input (see 'help raw-input'.)

Syntax: testCommand1
 usage: testCommand1 magic_number

Positional arguments:
  magic_number  Help on magic.

(lldb) testCommand1
usage: testCommand1 magic_number
testCommand1: error: the following arguments are required: magic_number

(lldb) testCommand1 42
The answer is 42
```

## Arguments, options, and subcommands

You can add positional arguments, optional arguments (options), and subcommands to
your command.  The arguments and options are added as described in the
documentation for the
[argparse](https://docs.python.org/3/library/argparse.html#the-add-argument-method)
module.  To add subcommands, use `add_subcommands` method as follows:

```python
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
```

Assuming the file is saved as
[examples/test_command2.py](examples/test_command2.py), you can import and run it
as follows:
```lldb
$ lldb

(lldb) command script import examples/test_command2.py

(lldb) help testCommand2
     Help on testCommand2.  Expects 'raw' input (see 'help raw-input'.)

Syntax: testCommand2
 usage: testCommand2 <subcommand> ...

The following subcommands are supported:
  <subcommand>
    subcommand1
                Help on subcommand1.
    subcommand2
                Help on subcommand2.

For more help on any particular subcommand, type 'testCommand2 <subcommand> --help'.

(lldb) testCommand2 subcommand1
Hello from subcommand1
```

## Contributing

Feel free to file an issue, or send a pull request.

Before making your changes, you need to establish a development environment.
As this repository is meant to be a submodule of
[lldb-bundle](//github.com/anpol/lldb-bundle), look there for creating the
Python virtual environment suitable for developing with LLDB.

Once you activated the virtual environment, run:
```sh
make init
```
to install the required development tools.

Use your editor or IDE to make your changes.  Add relevant tests.  To prepare
for a submission, run:
```sh
make format
make lint
make test
```

Fix lint issues and test failures.

Repeat until everything is OK, then open a pull request.

Thanks!

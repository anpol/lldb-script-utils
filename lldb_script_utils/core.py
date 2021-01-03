#!/usr/bin/env python
"""Utilities for creating LLDB `command script add` command strings."""

import shlex
from types import FunctionType
from typing import Optional, Literal, Union, Callable


def format_fully_qualified_type_name(
        type_object: Union[Callable, type]) -> str:
    """Formats a fully qualified name of any type."""
    module: str = type_object.__module__
    type_name: str = type_object.__qualname__
    if module is None or module == object.__module__:
        return type_name
    return f'{module}.{type_name}'


# noinspection PyShadowingBuiltins
def format_command_script_add(
    command_name: str,
    command_handler: Union[Callable, type],
    *,
    help: Optional[str] = None,  # pylint: disable=redefined-builtin
    synchronicity: Optional[Literal['synchronous', 'asynchronous',
                                    'current']] = None
) -> str:
    """Formats a `command script add` command line for use with LLDB."""
    result = [
        'command script add', '--function' if isinstance(
            command_handler, FunctionType) else '--class',
        format_fully_qualified_type_name(command_handler)
    ]
    if help is not None:
        result += ['--help', shlex.quote(help)]
    if synchronicity is not None:
        result += ['--synchronicity', synchronicity]
    result.append(command_name)
    return ' '.join(result)

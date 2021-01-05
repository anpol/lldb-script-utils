#!/usr/bin/env python
"""Utilities for creating LLDB `command script add` command strings."""

import shlex
from types import FunctionType
from typing import Optional, Literal, Union, Callable

import lldb


def format_fully_qualified_type_name(
        type_object: Union[Callable, type]) -> str:
    """Formats a fully qualified name of any type."""
    module: str = type_object.__module__
    type_name: str = type_object.__qualname__
    if module is None or module == object.__module__:
        return type_name
    return f'{module}.{type_name}'


# noinspection PyShadowingBuiltins
def handle_command_script_add(
    debugger: lldb.SBDebugger,
    command_name: str,
    command_handler: Union[Callable, type],
    *,
    help: Optional[str] = None,  # pylint: disable=redefined-builtin
    synchronicity: Optional[Literal['synchronous', 'asynchronous',
                                    'current']] = None
) -> None:
    """Make the debugger handle a formatted `command script add` command."""
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
    debugger.HandleCommand(' '.join(result))


def handle_type_summary_add(debugger: lldb.SBDebugger,
                            type_name: str,
                            *type_names: str,
                            inline_children: bool = False,
                            omit_names: bool = False,
                            expand: bool = False,
                            hide_empty: bool = False,
                            skip_pointers: bool = False,
                            skip_references: bool = False,
                            no_value: bool = False,
                            regex: bool = False,
                            summary_string: Optional[str] = None,
                            cascade: Optional[bool] = None,
                            python_function: Optional[Callable[
                                [lldb.SBValue, dict], str]] = None,
                            python_script: Optional[str] = None,
                            category: Optional[str] = None,
                            name: Optional[str] = None) -> None:
    """Make the debugger handle a formatted `type summary add` command."""
    result = ['type summary add']
    if inline_children:
        result.append('--inline-children')
    if omit_names:
        result.append('--omit-names')
    if expand:
        result.append('--expand')
    if hide_empty:
        result.append('--hide-empty')
    if skip_pointers:
        result.append('--skip-pointers')
    if skip_references:
        result.append('--skip-references')
    if no_value:
        result.append('--no-value')
    if regex:
        result.append('--regex')
    if summary_string is not None:
        result.append('--summary-string')
        result.append(shlex.quote(summary_string))
    if cascade is not None:
        result.append('--cascade')
        result.append(str(cascade).lower())
    if python_function is not None:
        result.append('--python-function')
        result.append(format_fully_qualified_type_name(python_function))
    if python_script is not None:
        result.append('--python-script')
        result.append(shlex.quote(python_script))
    if category is not None:
        result.append('--category')
        result.append(shlex.quote(category))
    if name is not None:
        result.append('--name')
        result.append(shlex.quote(name))
    result.append(shlex.quote(type_name))
    result.extend(shlex.quote(type_name) for type_name in type_names)
    debugger.HandleCommand(' '.join(result))


def handle_type_synthetic_add(debugger: lldb.SBDebugger,
                              type_name: str,
                              *type_names: str,
                              skip_pointers: bool = False,
                              skip_references: bool = False,
                              regex: bool = False,
                              cascade: Optional[bool] = None,
                              category: Optional[str] = None,
                              python_class: Optional[type] = None) -> None:
    """Make the debugger handle a formatted `type synthetic add` command."""
    result = ['type synthetic add']
    if skip_pointers:
        result.append('--skip-pointers')
    if skip_references:
        result.append('--skip-references')
    if regex:
        result.append('--regex')
    if cascade is not None:
        result.append('--cascade')
        result.append(str(cascade).lower())
    if category is not None:
        result.append('--category')
        result.append(shlex.quote(category))
    if python_class is not None:
        result.append('--python-class')
        result.append(format_fully_qualified_type_name(python_class))
    result.append(shlex.quote(type_name))
    result.extend(shlex.quote(type_name) for type_name in type_names)
    debugger.HandleCommand(' '.join(result))

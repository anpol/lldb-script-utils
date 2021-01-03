#!/usr/bin/env python
"""Utilities for creating LLDB `command script add` command strings."""

import shlex
from abc import ABC, abstractmethod
from types import FunctionType
from typing import Optional, Literal, Union, Callable

import lldb


def format_fully_qualified_type_name(type_object: type) -> str:
    """Formats a fully qualified name of any type."""
    module: str = type_object.__module__
    type_name: str = type_object.__qualname__
    if module is None or module == object.__module__:
        return type_name
    return f'{module}.{type_name}'


def format_command_script_add(
    command_name: str,
    command_handler: Union[Callable, type],
    short_help: Optional[str] = None,
    synchronicity: Optional[Literal['synchronous', 'asynchronous',
                                    'current']] = None
) -> str:
    """Formats a `command script add` command line for use with LLDB."""
    result = [
        'command script add',
        '-f' if isinstance(command_handler, FunctionType) else '-c',
        format_fully_qualified_type_name(command_handler)
    ]
    if short_help is not None:
        result += ['-h', shlex.quote(short_help)]
    if synchronicity is not None:
        result += ['-s', synchronicity]
    result.append(command_name)
    return ' '.join(result)


class LLDBCommand(ABC):
    """LLDB Command protocol.

    See `CommandObjectType` <https://lldb.llvm.org/use/python-reference.html>.
    """
    @abstractmethod
    def __init__(self, debugger: lldb.SBDebugger, bindings: dict):
        pass

    @abstractmethod
    def __call__(self, debugger: lldb.SBDebugger, command: str,
                 execution_context: lldb.SBExecutionContext,
                 command_return: lldb.SBCommandReturnObject) -> None:
        pass

    @abstractmethod
    def get_short_help(self) -> str:
        return ''

    @abstractmethod
    def get_long_help(self) -> str:
        return ''

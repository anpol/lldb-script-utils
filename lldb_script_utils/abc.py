#!/usr/bin/env python
"""Abstract base classes defined by LLDB for Python scripting."""

from abc import ABC, abstractmethod

import lldb


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

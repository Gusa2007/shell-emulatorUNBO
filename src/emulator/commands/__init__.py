"""Встроенные команды эмулятора.

Команды регистрируются в :data:`REGISTRY` при импорте модулей
:mod:`~emulator.commands.fs` и :mod:`~emulator.commands.session`.
"""

from emulator.commands import fs, session
from emulator.commands.registry import (
    REGISTRY, Command, CommandError, command, parse_flags)

__all__ = ["REGISTRY", "Command", "CommandError", "command",
           "parse_flags", "fs", "session"]

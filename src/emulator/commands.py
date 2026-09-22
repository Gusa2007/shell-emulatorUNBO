"""Встроенные команды эмулятора.

Каждая команда -- функция ``handler(shell, args)``, зарегистрированная
декоратором :func:`command`. Ошибки выполнения сообщаются исключением
:class:`CommandError`; оболочка выводит их в формате ``имя: сообщение``.
"""

from dataclasses import dataclass

EXIT_SUCCESS = 0
MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды (неверные аргументы и т.п.)."""


@dataclass(frozen=True)
class Command:
    """Описание встроенной команды."""

    name: str
    handler: object
    summary: str
    usage: str


REGISTRY = {}


def command(name, summary, usage):
    """Декоратор, регистрирующий функцию как команду ``name``."""
    def register(handler):
        REGISTRY[name] = Command(name, handler, summary, usage)
        return handler
    return register


@command("ls", "вывести содержимое каталога", "ls [путь...]")
def cmd_ls(shell, args):
    """Заглушка: вывести имя команды и её аргументы."""
    shell.write(f"ls: аргументы {args}")


@command("cd", "сменить текущий каталог", "cd [путь]")
def cmd_cd(shell, args):
    """Заглушка: вывести имя команды и её аргументы."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("слишком много аргументов")
    shell.write(f"cd: аргументы {args}")


@command("exit", "завершить работу эмулятора", "exit [код]")
def cmd_exit(shell, args):
    """Завершить работу оболочки с необязательным кодом возврата."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("слишком много аргументов")
    code = EXIT_SUCCESS
    if args:
        try:
            code = int(args[0])
        except ValueError as exc:
            raise CommandError(
                f"{args[0]}: требуется числовой аргумент") from exc
    shell.stop(code)

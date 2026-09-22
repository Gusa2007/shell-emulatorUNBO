"""Реестр встроенных команд и общие вспомогательные функции.

Каждая команда -- функция ``handler(shell, args)``, зарегистрированная
декоратором :func:`command`. Ошибка выполнения сообщается исключением
:class:`CommandError`, оболочка выводит её как ``имя: сообщение``.
Если команда уже сама вывела сообщения об ошибках, она возвращает
``False``.
"""

from dataclasses import dataclass

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"


class CommandError(Exception):
    """Ошибка выполнения команды (неверные аргументы и т.п.)."""


@dataclass(frozen=True)
class Command:
    """Описание встроенной команды для справки и выполнения."""

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


def is_option(arg):
    """Является ли аргумент набором ключей вида ``-la``."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def parse_flags(args, allowed):
    """Отделить однобуквенные ключи от операндов.

    ``allowed`` -- строка допустимых букв. Возвращает пару
    (множество ключей, список операндов). ``--`` завершает ключи.
    """
    flags = set()
    operands = []
    options_done = False
    for arg in args:
        if options_done or not is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            flags.update(_check_flags(arg[1:], allowed))
    return flags, operands


def _check_flags(letters, allowed):
    """Проверить, что все буквы ключа допустимы."""
    for letter in letters:
        if letter not in allowed:
            raise CommandError(f"неверный ключ -- '{letter}'")
    return set(letters)


def parse_count(text):
    """Разобрать неотрицательное целое число из аргумента."""
    if not text.isdigit():
        raise CommandError(f"{text}: требуется числовой аргумент")
    return int(text)

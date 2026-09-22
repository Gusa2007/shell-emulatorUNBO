"""Команды управления сеансом: exit, who, history, help."""

from emulator.commands.registry import (
    REGISTRY, CommandError, command, parse_count, parse_flags)

EXIT_SUCCESS = 0
MAX_EXIT_ARGS = 1
MAX_HISTORY_ARGS = 1
WHO_TERMINAL = "pts/0"
WHO_HOST = "(:0)"
WHO_TIME_FORMAT = "%Y-%m-%d %H:%M"
WHO_HEADER = ("ИМЯ", "ЛИНИЯ", "ВРЕМЯ", "КОММЕНТАРИЙ")
WHO_AM_I = ["am", "i"]
NAME_WIDTH = 8
LINE_WIDTH = 12
TIME_WIDTH = 16
NUMBER_WIDTH = 5
USAGE_WIDTH = 30
MAX_HELP_ARGS = 1


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


def _who_row(name, line, time, comment):
    """Отформатировать строку таблицы who."""
    return (f"{name:<{NAME_WIDTH}} {line:<{LINE_WIDTH}} "
            f"{time:<{TIME_WIDTH}} {comment}")


@command("who", "показать, кто работает в системе",
         "who [-H] [-q] [am i]")
def cmd_who(shell, args):
    """Вывести пользователей сеанса: -H -- заголовок, -q -- счётчик."""
    flags, operands = parse_flags(args, "Hq")
    if operands and operands != WHO_AM_I:
        raise CommandError(f"лишний операнд '{operands[0]}'")
    if "q" in flags:
        users = [shell.user]
        shell.write(" ".join(users))
        shell.write(f"# пользователей={len(users)}")
        return
    if "H" in flags:
        shell.write(_who_row(*WHO_HEADER))
    started = shell.started.strftime(WHO_TIME_FORMAT)
    shell.write(_who_row(shell.user, WHO_TERMINAL, started, WHO_HOST))


@command("history", "показать историю введённых команд",
         "history [-c] [N]")
def cmd_history(shell, args):
    """Вывести историю; N -- последние N команд, -c -- очистить."""
    flags, operands = parse_flags(args, "c")
    if len(operands) > MAX_HISTORY_ARGS:
        raise CommandError("слишком много аргументов")
    if "c" in flags:
        shell.history.clear()
        return
    count = parse_count(operands[0]) if operands else len(shell.history)
    start = len(shell.history) - count
    for number, line in enumerate(shell.history, start=1):
        if number > start:
            shell.write(f"{number:>{NUMBER_WIDTH}}  {line}")


@command("help", "показать список команд или справку по команде",
         "help [команда]")
def cmd_help(shell, args):
    """Вывести список команд с описанием или справку по одной."""
    if len(args) > MAX_HELP_ARGS:
        raise CommandError("слишком много аргументов")
    if args:
        cmd = REGISTRY.get(args[0])
        if cmd is None:
            raise CommandError(f"нет справки по '{args[0]}'")
        shell.write(f"{cmd.name}: {cmd.usage}")
        shell.write(f"    {cmd.summary}.")
        shell.write(f"    {cmd.handler.__doc__.strip()}")
        return
    shell.write("Встроенные команды:")
    for name in sorted(REGISTRY):
        cmd = REGISTRY[name]
        shell.write(f"  {cmd.usage:<{USAGE_WIDTH}} {cmd.summary}")

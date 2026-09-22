"""Ядро эмулятора: разбор и выполнение команд без привязки к GUI."""

from emulator import system
from emulator.commands import REGISTRY, CommandError
from emulator.parser import ParseError, parse

SHELL_NAME = "emu"
OUT = "out"
ERR = "err"
ECHO = "echo"


def _print_output(text, kind):
    """Вывод по умолчанию -- в стандартный поток."""
    print(text)


class Shell:
    """Состояние сеанса оболочки и выполнение команд.

    ``output`` -- функция ``output(text, kind)``, куда отправляется
    весь вывод; ``kind`` -- один из ``"out"``, ``"err"``, ``"echo"``.
    """

    def __init__(self, output=None):
        """Создать сеанс для текущего пользователя ОС."""
        self.output = output or _print_output
        self.user = system.get_username()
        self.host = system.get_hostname()
        self.cwd = "/"
        self.running = True
        self.exit_code = 0

    @property
    def title(self):
        """Заголовок окна на основе данных реальной ОС."""
        return system.window_title(self.user, self.host)

    def prompt(self):
        """Строка приглашения, например ``user@host:/$ ``."""
        return f"{self.user}@{self.host}:{self.cwd}$ "

    def write(self, text):
        """Вывести обычный текст."""
        self.output(text, OUT)

    def error(self, text):
        """Вывести сообщение об ошибке."""
        self.output(text, ERR)

    def stop(self, code):
        """Завершить сеанс с кодом ``code``."""
        self.running = False
        self.exit_code = code

    def execute(self, line):
        """Выполнить одну строку ввода.

        Возвращает ``True``, если команда выполнена без ошибок.
        """
        try:
            words = parse(line)
        except ParseError as exc:
            self.error(f"{SHELL_NAME}: синтаксическая ошибка: {exc}")
            return False
        if not words:
            return True
        return self._run(words[0], words[1:])

    def _run(self, name, args):
        """Найти команду ``name`` и выполнить её с аргументами."""
        cmd = REGISTRY.get(name)
        if cmd is None:
            self.error(f"{SHELL_NAME}: {name}: команда не найдена")
            return False
        try:
            cmd.handler(self, args)
        except CommandError as exc:
            self.error(f"{name}: {exc}")
            return False
        return True

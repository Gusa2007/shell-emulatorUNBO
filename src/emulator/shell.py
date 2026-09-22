"""Ядро эмулятора: разбор и выполнение команд без привязки к GUI."""

from emulator import system
from emulator.commands import REGISTRY, CommandError
from emulator.parser import ParseError, parse
from emulator.vfs import VFS, VFSError

SHELL_NAME = "emu"
OUT = "out"
ERR = "err"
ECHO = "echo"
DEBUG = "debug"


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
        self.vfs = VFS()
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

    def debug(self, text):
        """Вывести отладочное сообщение."""
        self.output(text, DEBUG)

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

    def start(self, config):
        """Выполнить действия при запуске согласно настройкам ``config``."""
        for line in config.describe():
            self.debug(line)
        if config.vfs_path:
            self.load_vfs(config.vfs_path)
        self.show_motd()
        if config.script_path:
            self.run_script(config.script_path)

    def load_vfs(self, path):
        """Загрузить VFS из ZIP-архива; при ошибке оставить пустую."""
        try:
            self.vfs = VFS.from_zip(path)
        except VFSError as exc:
            self.error(f"{SHELL_NAME}: ошибка загрузки VFS: {exc}")
            return False
        self.cwd = "/"
        dirs, files = self.vfs.stats()
        self.debug(f"[debug] VFS загружена из {path}: "
                   f"каталогов {dirs}, файлов {files}")
        return True

    def show_motd(self):
        """Вывести сообщение дня из файла /motd, если он есть."""
        text = self.vfs.motd()
        if text is not None:
            self.write(text.rstrip("\n"))

    def run_script(self, path):
        """Выполнить стартовый скрипт, показывая ввод и вывод.

        Выполнение продолжается после ошибок; в конце выводится
        число строк с ошибками. Возвращает ``True``, если ошибок нет.
        """
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            self.error(f"{SHELL_NAME}: {path}: не удалось прочитать "
                       f"скрипт: {exc}")
            return False
        failed = self._run_lines(lines)
        self.debug(f"[debug] скрипт {path} выполнен, "
                   f"строк с ошибками: {len(failed)}")
        return not failed

    def _run_lines(self, lines):
        """Выполнить строки скрипта и вернуть номера строк с ошибками."""
        failed = []
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            if not line.strip():
                continue
            self.output(self.prompt() + line, ECHO)
            if not self.execute(line):
                failed.append(number)
        return failed

"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Настройки, заданные пользователем при запуске."""

    vfs_path: str = None
    script_path: str = None

    def describe(self):
        """Вернуть строки отладочного вывода всех параметров."""
        return [
            f"[debug] vfs_path    = {self.vfs_path!r}",
            f"[debug] script_path = {self.script_path!r}",
        ]


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="GUI-эмулятор командной оболочки UNIX-подобной ОС")
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS (ZIP-архив)")
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту с командами эмулятора")
    return parser


def parse_args(argv=None):
    """Разобрать аргументы ``argv`` и вернуть :class:`Config`."""
    namespace = build_parser().parse_args(argv)
    return Config(vfs_path=namespace.vfs_path,
                  script_path=namespace.script_path)

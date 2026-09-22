"""Сведения о реальной ОС, в которой запущен эмулятор."""

import getpass
import os
import socket

UNKNOWN_USER = "user"
UNKNOWN_HOST = "localhost"


def get_username():
    """Вернуть имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (OSError, KeyError):
        return os.environ.get("USERNAME", UNKNOWN_USER)


def get_hostname():
    """Вернуть сетевое имя компьютера."""
    return socket.gethostname() or UNKNOWN_HOST


def window_title(user, host):
    """Сформировать заголовок окна вида ``Эмулятор - [user@host]``."""
    return f"Эмулятор - [{user}@{host}]"

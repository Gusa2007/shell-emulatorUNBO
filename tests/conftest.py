"""Общие фикстуры тестов."""

import pytest

from emulator.shell import Shell


class Recorder:
    """Собирает вывод оболочки для проверок."""

    def __init__(self):
        """Создать пустой журнал вывода."""
        self.lines = []

    def __call__(self, text, kind):
        """Сохранить строку вывода вместе с её видом."""
        self.lines.append((kind, text))

    def text(self, kind=None):
        """Вернуть весь вывод (или вывод одного вида) одной строкой."""
        return "\n".join(t for k, t in self.lines if kind in (None, k))


@pytest.fixture
def recorder():
    """Журнал вывода."""
    return Recorder()


@pytest.fixture
def shell(recorder):
    """Оболочка, пишущая вывод в журнал."""
    return Shell(output=recorder)

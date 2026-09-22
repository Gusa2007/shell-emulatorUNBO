"""Общие фикстуры тестов."""

import zipfile

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


TREE = {
    "motd": "Добро пожаловать!\n",
    "home/user/docs/reports/q1.txt": "отчёт",
    "home/user/docs/empty/": "",
    "home/user/My Documents/letter.txt": "письмо",
    "home/user/.profile": "PATH=/bin",
    "etc/hosts": "127.0.0.1 localhost",
    "tmp/": "",
}


@pytest.fixture
def vfs_zip(tmp_path):
    """ZIP-архив с тестовым деревом VFS."""
    path = tmp_path / "vfs.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in TREE.items():
            archive.writestr(name, data)
    return str(path)


@pytest.fixture
def vfs_shell(shell, recorder, vfs_zip):
    """Оболочка с загруженной VFS и очищенным журналом вывода."""
    shell.load_vfs(vfs_zip)
    recorder.lines.clear()
    return shell

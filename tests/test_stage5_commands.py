"""Тесты команд rmdir и help (этап 5)."""

import zipfile

import pytest

from emulator.commands import REGISTRY
from emulator.vfs import VFSError


def test_rmdir_empty_dir(vfs_shell, recorder):
    """Пустой каталог удаляется."""
    assert vfs_shell.execute("rmdir /tmp")
    with pytest.raises(VFSError):
        vfs_shell.vfs.lookup("/tmp")
    assert recorder.text("err") == ""


def test_rmdir_relative_and_several(vfs_shell):
    """Несколько каталогов и относительные пути."""
    vfs_shell.execute("cd /home/user")
    vfs_shell.execute("rmdir docs/empty /tmp")
    vfs_shell.execute("ls docs")
    assert "empty" not in vfs_shell.vfs.lookup("/home/user/docs").children
    assert "tmp" not in vfs_shell.vfs.root.children


def test_rmdir_parents_stops_at_non_empty(vfs_shell, recorder):
    """Ключ -p останавливается на первом непустом родителе."""
    assert not vfs_shell.execute("rmdir -p /home/user/docs/empty")
    docs = vfs_shell.vfs.lookup("/home/user/docs")
    assert "empty" not in docs.children
    assert "'/home/user/docs': Каталог не пуст" in recorder.text("err")


def test_rmdir_parents_chain(shell, tmp_path):
    """Ключ -p на цепочке пустых каталогов удаляет её целиком."""
    path = tmp_path / "chain.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("a/b/c/", "")
        archive.writestr("keep.txt", "x")
    shell.load_vfs(str(path))
    assert shell.execute("rmdir -p a/b/c")
    assert list(shell.vfs.root.children) == ["keep.txt"]


def test_rmdir_errors(vfs_shell, recorder):
    """Ошибки: не пуст, не каталог, нет каталога, занят, нет операнда."""
    vfs_shell.execute("cd /home/user/docs/empty")
    commands = ["rmdir /home/user/docs", "rmdir /etc/hosts",
                "rmdir /nope", "rmdir .", "rmdir /", "rmdir",
                "rmdir -x /tmp"]
    for line in commands:
        assert not vfs_shell.execute(line)
    errors = recorder.text("err")
    assert "'/home/user/docs': Каталог не пуст" in errors
    assert "'/etc/hosts': Это не каталог" in errors
    assert "'/nope': Нет такого файла или каталога" in errors
    assert "'.': Устройство или ресурс занято" in errors
    assert "'/': Каталог не пуст" in errors
    assert "rmdir: пропущен операнд" in errors
    assert "rmdir: неверный ключ -- 'x'" in errors
    assert vfs_shell.vfs.lookup("/tmp").is_dir


def test_rmdir_does_not_touch_archive(vfs_shell, vfs_zip):
    """Изменения только в памяти: архив остаётся прежним."""
    with open(vfs_zip, "rb") as file:
        before = file.read()
    vfs_shell.execute("rmdir /tmp")
    with open(vfs_zip, "rb") as file:
        assert file.read() == before
    with zipfile.ZipFile(vfs_zip) as archive:
        assert "tmp/" in archive.namelist()


def test_help_lists_all_commands(shell, recorder):
    """Команда help перечисляет все команды с описанием."""
    assert shell.execute("help")
    text = recorder.text("out")
    for cmd in REGISTRY.values():
        assert cmd.usage in text
        assert cmd.summary in text
    expected = {"ls", "cd", "exit", "who", "history", "rmdir", "help"}
    assert expected <= set(REGISTRY)


def test_help_for_one_command(shell, recorder):
    """Команда help ИМЯ выводит справку по одной команде."""
    assert shell.execute("help rmdir")
    lines = recorder.text("out").splitlines()
    assert lines[0] == "rmdir: rmdir [-p] каталог..."
    assert "-p" in lines[2]


def test_help_errors(shell, recorder):
    """Неизвестная команда и лишние аргументы -- ошибки."""
    assert not shell.execute("help nope")
    assert not shell.execute("help ls cd")
    assert "help: нет справки по 'nope'" in recorder.text("err")
    assert "слишком много аргументов" in recorder.text("err")

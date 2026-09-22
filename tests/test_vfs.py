"""Тесты виртуальной файловой системы (этап 3)."""

import base64
import zipfile

import pytest

import make_vfs
from emulator.config import Config
from emulator.vfs import VFS, VFSError, normalize

PNG_BYTES = b"\x89PNG\r\n\x1a\n\0\0"


def make_zip(path, entries):
    """Создать ZIP-архив из словаря ``имя -> содержимое``."""
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return str(path)


@pytest.fixture
def deep_zip(tmp_path):
    """Архив с деревом из нескольких уровней и двоичным файлом."""
    return make_zip(tmp_path / "deep.zip", {
        "motd": "Привет!\n",
        "a/b/c/file.txt": "текст",
        "a/empty/": "",
        "bin/logo.png": PNG_BYTES,
    })


@pytest.mark.parametrize("path, cwd, expected", [
    ("/a/b", "/", "/a/b"),
    ("b", "/a", "/a/b"),
    ("../c", "/a/b", "/a/c"),
    ("./x/./y/", "/", "/x/y"),
    ("../../..", "/a", "/"),
    ("", "/a", "/a"),
])
def test_normalize(path, cwd, expected):
    """Нормализация путей с . и .. ."""
    assert normalize(path, cwd) == expected


def test_load_tree(deep_zip):
    """Все уровни дерева и пустые каталоги загружаются."""
    vfs = VFS.from_zip(deep_zip)
    assert vfs.lookup("/a/b/c/file.txt").text() == "текст"
    assert vfs.lookup("/a/empty").is_dir
    assert vfs.lookup("c/file.txt", "/a/b").path == "/a/b/c/file.txt"
    assert vfs.stats() == (5, 3)


def test_binary_file_as_base64(deep_zip):
    """Двоичные данные хранятся байтами и выводятся в base64."""
    node = VFS.from_zip(deep_zip).lookup("/bin/logo.png")
    assert node.is_binary
    assert node.data == PNG_BYTES
    assert base64.b64decode(node.text()) == PNG_BYTES


def test_archive_is_not_modified(deep_zip):
    """Загрузка VFS не изменяет исходный архив."""
    with open(deep_zip, "rb") as file:
        before = file.read()
    VFS.from_zip(deep_zip).root.children.clear()
    with open(deep_zip, "rb") as file:
        assert file.read() == before


def test_lookup_errors(deep_zip):
    """Несуществующий путь и путь через файл -- ошибки."""
    vfs = VFS.from_zip(deep_zip)
    with pytest.raises(VFSError, match="Нет такого файла"):
        vfs.lookup("/nope")
    with pytest.raises(VFSError, match="Это не каталог"):
        vfs.lookup("/motd/x")


@pytest.mark.parametrize("content", [None, b"not a zip"])
def test_bad_sources(tmp_path, content):
    """Отсутствующий файл и не-архив -- ошибки загрузки."""
    path = tmp_path / "vfs.zip"
    if content is not None:
        path.write_bytes(content)
    with pytest.raises(VFSError):
        VFS.from_zip(str(path))


def test_unsafe_path_rejected(tmp_path):
    """Пути с .. в архиве отвергаются."""
    path = make_zip(tmp_path / "bad.zip", {"../evil": "x"})
    with pytest.raises(VFSError, match="недопустимый путь"):
        VFS.from_zip(path)


def test_empty_archive_has_no_motd(tmp_path):
    """Пустой архив даёт пустую VFS без motd."""
    vfs = VFS.from_zip(make_zip(tmp_path / "e.zip", {}))
    assert vfs.stats() == (0, 0)
    assert vfs.motd() is None


def test_motd_shown_on_start(shell, recorder, deep_zip):
    """При запуске выводится motd из корня VFS."""
    shell.start(Config(vfs_path=deep_zip))
    assert ("out", "Привет!") in recorder.lines
    assert "каталогов 5, файлов 3" in recorder.text("debug")


def test_bad_vfs_reported_on_start(shell, recorder, tmp_path):
    """Ошибка загрузки VFS сообщается, оболочка продолжает работу."""
    shell.start(Config(vfs_path=str(tmp_path / "none.zip")))
    assert "ошибка загрузки VFS" in recorder.text("err")
    assert shell.running


def test_make_vfs_tool(tmp_path):
    """Сборщик архивов декодирует .b64 и пропускает .keep."""
    source = tmp_path / "src"
    (source / "empty").mkdir(parents=True)
    (source / "empty" / ".keep").write_text("")
    (source / "img.b64").write_bytes(base64.b64encode(PNG_BYTES))
    target = make_vfs.build(source, tmp_path / "out.zip")
    vfs = VFS.from_zip(str(target))
    assert vfs.lookup("/img").data == PNG_BYTES
    assert vfs.lookup("/empty").children == {}

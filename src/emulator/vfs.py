"""Виртуальная файловая система (VFS), целиком хранящаяся в памяти.

Источник VFS -- ZIP-архив. Архив только читается: его содержимое
копируется в дерево объектов :class:`Directory` и :class:`File`,
все дальнейшие изменения происходят лишь в памяти. Содержимое файлов
хранится как ``bytes``; двоичные данные при выводе представляются
в кодировке base64.
"""

import base64
import datetime
import zipfile

SEPARATOR = "/"
ROOT = "/"
CURRENT = "."
PARENT = ".."
MOTD_NAME = "motd"
TEXT_ENCODING = "utf-8"
NUL_BYTE = b"\0"
DEFAULT_MTIME = datetime.datetime(1980, 1, 1)


class VFSError(Exception):
    """Ошибка работы с VFS (нет файла, не каталог, битый архив...)."""


class Node:
    """Общая часть файла и каталога."""

    def __init__(self, name, parent=None, mtime=DEFAULT_MTIME):
        """Создать узел с именем ``name`` внутри каталога ``parent``."""
        self.name = name
        self.parent = parent
        self.mtime = mtime

    @property
    def path(self):
        """Абсолютный путь узла внутри VFS."""
        if self.parent is None:
            return ROOT
        parent_path = self.parent.path.rstrip(SEPARATOR)
        return f"{parent_path}{SEPARATOR}{self.name}"

    @property
    def is_dir(self):
        """Является ли узел каталогом."""
        return False


class File(Node):
    """Обычный файл с содержимым в памяти."""

    def __init__(self, name, parent, data=b"", mtime=DEFAULT_MTIME):
        """Создать файл с двоичным содержимым ``data``."""
        super().__init__(name, parent, mtime)
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)

    @property
    def is_binary(self):
        """Содержит ли файл двоичные (не текстовые) данные."""
        if NUL_BYTE in self.data:
            return True
        try:
            self.data.decode(TEXT_ENCODING)
        except UnicodeDecodeError:
            return True
        return False

    def text(self):
        """Вернуть содержимое как текст; двоичное -- в base64."""
        if self.is_binary:
            return base64.b64encode(self.data).decode("ascii")
        return self.data.decode(TEXT_ENCODING)


class Directory(Node):
    """Каталог: словарь дочерних узлов по именам."""

    def __init__(self, name, parent=None, mtime=DEFAULT_MTIME):
        """Создать пустой каталог."""
        super().__init__(name, parent, mtime)
        self.children = {}

    @property
    def is_dir(self):
        """Является ли узел каталогом."""
        return True

    def add(self, node):
        """Добавить дочерний узел и вернуть его."""
        node.parent = self
        self.children[node.name] = node
        return node


def split_path(path):
    """Разбить путь на непустые компоненты."""
    return [part for part in path.split(SEPARATOR) if part]


def normalize(path, cwd=ROOT):
    """Преобразовать ``path`` в абсолютный путь без ``.`` и ``..``."""
    base = [] if path.startswith(SEPARATOR) else split_path(cwd)
    parts = list(base)
    for part in split_path(path):
        if part == PARENT:
            if parts:
                parts.pop()
        elif part != CURRENT:
            parts.append(part)
    return ROOT + SEPARATOR.join(parts)


class VFS:
    """Дерево файлов и каталогов в памяти."""

    def __init__(self, source=None):
        """Создать пустую VFS; ``source`` -- откуда она загружена."""
        self.root = Directory("")
        self.source = source

    @classmethod
    def from_zip(cls, path):
        """Загрузить VFS из ZIP-архива ``path`` (архив не изменяется)."""
        vfs = cls(source=path)
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    vfs._load_entry(archive, info)
        except FileNotFoundError as exc:
            raise VFSError(f"{path}: файл не найден") from exc
        except (zipfile.BadZipFile, IsADirectoryError) as exc:
            raise VFSError(f"{path}: не является ZIP-архивом") from exc
        except OSError as exc:
            raise VFSError(f"{path}: {exc}") from exc
        return vfs

    def _load_entry(self, archive, info):
        """Добавить в дерево одну запись архива."""
        parts = split_path(info.filename)
        if not parts:
            return
        if PARENT in parts:
            raise VFSError(f"недопустимый путь в архиве: {info.filename}")
        mtime = datetime.datetime(*info.date_time)
        if info.is_dir():
            self._make_dirs(parts).mtime = mtime
            return
        parent = self._make_dirs(parts[:-1])
        if parts[-1] in parent.children:
            raise VFSError(f"повторяющийся путь в архиве: {info.filename}")
        parent.add(File(parts[-1], parent, archive.read(info), mtime))

    def _make_dirs(self, parts):
        """Вернуть каталог по компонентам пути, создавая недостающие."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = node.add(Directory(part, node))
            elif not child.is_dir:
                raise VFSError(f"{child.path}: конфликт файла и каталога")
            node = child
        return node

    def lookup(self, path, cwd=ROOT):
        """Найти узел по пути (абсолютному или относительно ``cwd``)."""
        node = self.root
        for part in split_path(normalize(path, cwd)):
            if not node.is_dir:
                raise VFSError(f"{path}: Это не каталог")
            node = node.children.get(part)
            if node is None:
                raise VFSError(f"{path}: Нет такого файла или каталога")
        return node

    def motd(self):
        """Вернуть текст файла motd из корня VFS или ``None``."""
        node = self.root.children.get(MOTD_NAME)
        if node is None or node.is_dir:
            return None
        return node.text()

    def stats(self):
        """Вернуть пару (число каталогов, число файлов) без корня."""
        dirs = files = 0
        stack = [self.root]
        while stack:
            for child in stack.pop().children.values():
                if child.is_dir:
                    dirs += 1
                    stack.append(child)
                else:
                    files += 1
        return dirs, files

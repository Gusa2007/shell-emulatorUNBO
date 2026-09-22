"""Сборка ZIP-архивов VFS из каталогов с исходными данными.

Архивы в репозитории не хранятся: они собираются этим скриптом
из каталогов ``vfs/<имя>`` в ``build/vfs/<имя>.zip``.

Соглашения:

* файл ``.keep`` не попадает в архив -- он лишь сохраняет в git
  пустой каталог;
* файл ``имя.b64`` декодируется из base64 и кладётся в архив
  как двоичный файл ``имя``.
"""

import base64
import pathlib
import sys
import zipfile

KEEP_FILE = ".keep"
BASE64_SUFFIX = ".b64"
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT_DIR / "vfs"
OUTPUT_DIR = ROOT_DIR / "build" / "vfs"
EXPECTED_ARGS = 2
USAGE = "использование: make_vfs.py [КАТАЛОГ АРХИВ]"


def entry_name(path, source):
    """Вернуть имя записи архива для файла ``path``."""
    relative = path.relative_to(source).as_posix()
    if path.suffix == BASE64_SUFFIX:
        return relative[:-len(BASE64_SUFFIX)]
    return relative


def entry_data(path):
    """Вернуть содержимое файла; ``.b64`` декодируется."""
    data = path.read_bytes()
    if path.suffix == BASE64_SUFFIX:
        return base64.b64decode(data)
    return data


def build(source, target):
    """Собрать архив ``target`` из каталога ``source``."""
    source = pathlib.Path(source)
    target = pathlib.Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source).as_posix()
            if path.is_dir():
                archive.writestr(relative + "/", b"")
            elif path.name != KEEP_FILE:
                archive.writestr(entry_name(path, source), entry_data(path))
    return target


def build_all():
    """Собрать архивы для всех каталогов из ``vfs/``."""
    for source in sorted(SOURCE_DIR.iterdir()):
        if source.is_dir():
            target = build(source, OUTPUT_DIR / f"{source.name}.zip")
            print(f"собран {target.relative_to(ROOT_DIR)}")


def main(argv):
    """Разобрать аргументы и собрать один или все архивы."""
    if not argv:
        build_all()
        return 0
    if len(argv) != EXPECTED_ARGS:
        print(USAGE, file=sys.stderr)
        return 1
    print(f"собран {build(argv[0], argv[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

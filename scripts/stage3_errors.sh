#!/bin/sh
# Этап 3: ошибки загрузки VFS (нет файла, не ZIP-архив).
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== несуществующий архив =="
./run.sh --vfs build/vfs/missing.zip
echo "== файл не является ZIP-архивом =="
./run.sh --vfs README.md

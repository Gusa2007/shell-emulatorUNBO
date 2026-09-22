#!/bin/sh
# Этап 3: VFS из нескольких файлов, в т.ч. двоичного.
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== несколько файлов =="
./run.sh --vfs build/vfs/few_files.zip --script examples/stage3.emu

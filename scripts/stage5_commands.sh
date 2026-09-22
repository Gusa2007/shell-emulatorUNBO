#!/bin/sh
# Этап 5: проверка команд rmdir и help на VFS deep.
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== rmdir, help =="
./run.sh --vfs build/vfs/deep.zip --script examples/stage5.emu

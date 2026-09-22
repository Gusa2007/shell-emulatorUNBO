#!/bin/sh
# Этап 2: несуществующий скрипт -- сообщение об ошибке.
cd "$(dirname "$0")/.." || exit 1
echo "== несуществующий скрипт =="
./run.sh --script examples/missing.emu

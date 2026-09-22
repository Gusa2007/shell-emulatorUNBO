#!/bin/sh
# Этап 2: задан только стартовый скрипт.
cd "$(dirname "$0")/.." || exit 1
echo "== только --script =="
./run.sh --script examples/stage2.emu

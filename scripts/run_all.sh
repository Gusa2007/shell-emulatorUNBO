#!/bin/sh
# Последовательный запуск демонстраций всех этапов.
cd "$(dirname "$0")" || exit 1
for script in stage*.sh; do
    echo "######## $script"
    sh "./$script"
done

"""Точка входа: запуск графического эмулятора оболочки."""

import sys

from emulator.gui import EmulatorApp
from emulator.shell import Shell


def main():
    """Создать оболочку, открыть окно и вернуть код завершения."""
    shell = Shell()
    app = EmulatorApp(shell)
    app.run()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())

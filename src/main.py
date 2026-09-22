"""Точка входа: запуск графического эмулятора оболочки."""

import sys

from emulator.config import parse_args
from emulator.gui import EmulatorApp
from emulator.shell import Shell


def main(argv=None):
    """Разобрать параметры, открыть окно и вернуть код завершения."""
    config = parse_args(argv)
    shell = Shell()
    app = EmulatorApp(shell)
    app.start(config)
    app.run()
    return shell.exit_code


if __name__ == "__main__":
    sys.exit(main())

"""Тесты ядра оболочки (этап 1)."""

from emulator.system import window_title


def test_title_uses_real_os_data(shell):
    """Заголовок окна строится из имени пользователя и хоста."""
    assert shell.title == f"Эмулятор - [{shell.user}@{shell.host}]"
    assert window_title("u", "h") == "Эмулятор - [u@h]"


def test_unknown_command(shell, recorder):
    """Неизвестная команда -- сообщение об ошибке."""
    assert not shell.execute("foo bar")
    assert "foo: команда не найдена" in recorder.text("err")


def test_syntax_error(shell, recorder):
    """Незакрытая кавычка -- синтаксическая ошибка."""
    assert not shell.execute('ls "abc')
    assert "синтаксическая ошибка" in recorder.text("err")


def test_empty_line_is_ok(shell, recorder):
    """Пустая строка ничего не делает."""
    assert shell.execute("   ")
    assert recorder.lines == []


def test_exit_default_code(shell):
    """Команда exit без аргументов завершает сеанс с кодом 0."""
    shell.execute("exit")
    assert not shell.running
    assert shell.exit_code == 0


def test_exit_with_code(shell):
    """Команда exit N завершает сеанс с кодом N."""
    code = 3
    shell.execute(f"exit {code}")
    assert shell.exit_code == code


def test_exit_bad_args(shell, recorder):
    """Нечисловой код и лишние аргументы -- ошибки, сеанс продолжается."""
    assert not shell.execute("exit abc")
    assert not shell.execute("exit 1 2")
    assert shell.running
    assert "требуется числовой аргумент" in recorder.text("err")
    assert "слишком много аргументов" in recorder.text("err")

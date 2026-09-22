"""Тесты команд-заглушек этапа 1."""


def test_ls_stub_prints_args(shell, recorder):
    """Заглушка ls печатает своё имя и аргументы."""
    assert shell.execute('ls -l "My Docs"')
    assert recorder.text() == "ls: аргументы ['-l', 'My Docs']"


def test_cd_stub_prints_args(shell, recorder):
    """Заглушка cd печатает своё имя и аргументы."""
    assert shell.execute("cd /tmp")
    assert recorder.text() == "cd: аргументы ['/tmp']"


def test_cd_stub_too_many_args(shell, recorder):
    """Команда cd с двумя аргументами -- ошибка."""
    assert not shell.execute("cd a b")
    assert recorder.text("err") == "cd: слишком много аргументов"

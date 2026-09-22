"""Тесты команд who и history (этап 4)."""


def out(recorder):
    """Вернуть строки обычного вывода."""
    return [text for kind, text in recorder.lines if kind == "out"]


def test_who(shell, recorder):
    """Команда who выводит текущего пользователя и терминал."""
    assert shell.execute("who")
    line = out(recorder)[0]
    assert line.startswith(shell.user)
    assert "pts/0" in line
    assert shell.started.strftime("%Y-%m-%d") in line


def test_who_modes(shell, recorder):
    """Режимы -H (заголовок), -q (счётчик) и am i."""
    shell.execute("who -H")
    shell.execute("who -q")
    shell.execute("who am i")
    lines = out(recorder)
    assert lines[0].startswith("ИМЯ")
    assert lines[2:4] == [shell.user, "# пользователей=1"]
    assert lines[4].startswith(shell.user)


def test_who_errors(shell, recorder):
    """Неверный ключ и лишний операнд -- ошибки."""
    assert not shell.execute("who -x")
    assert not shell.execute("who foo")
    assert "неверный ключ -- 'x'" in recorder.text("err")
    assert "лишний операнд 'foo'" in recorder.text("err")


def test_history_lists_all(shell, recorder):
    """Команда history нумерует все введённые строки, включая себя."""
    shell.execute("who -q")
    shell.execute("bad-cmd")
    shell.execute("   ")
    recorder.lines.clear()
    shell.execute("history")
    assert out(recorder) == [
        "    1  who -q", "    2  bad-cmd", "    3  history"]


def test_history_last_n(shell, recorder):
    """Команда history N выводит последние N строк."""
    for _ in range(3):
        shell.execute("who -q")
    recorder.lines.clear()
    shell.execute("history 2")
    assert out(recorder) == ["    3  who -q", "    4  history 2"]


def test_history_clear(shell, recorder):
    """Команда history -c очищает историю."""
    shell.execute("who")
    shell.execute("history -c")
    recorder.lines.clear()
    shell.execute("history")
    assert out(recorder) == ["    1  history"]


def test_history_errors(shell, recorder):
    """Нечисловой аргумент и лишние аргументы -- ошибки."""
    assert not shell.execute("history abc")
    assert not shell.execute("history 1 2")
    assert not shell.execute("history -5")
    errors = recorder.text("err")
    assert "history: abc: требуется числовой аргумент" in errors
    assert "слишком много аргументов" in errors
    assert "неверный ключ -- '5'" in errors


def test_script_commands_go_to_history(shell, tmp_path):
    """Команды скрипта попадают в историю, комментарии -- нет."""
    script = tmp_path / "s.emu"
    script.write_text("# comment\nwho\nls 'x\n", encoding="utf-8")
    shell.run_script(str(script))
    assert shell.history == ["who", "ls 'x"]

"""Тесты параметров командной строки и стартового скрипта (этап 2)."""

import pytest

from emulator.config import Config, parse_args
from emulator.parser import parse


def test_defaults():
    """Без параметров оба пути не заданы."""
    assert parse_args([]) == Config(None, None)


def test_all_params():
    """Оба параметра разбираются."""
    config = parse_args(["--vfs", "a.zip", "--script", "s.emu"])
    assert config == Config("a.zip", "s.emu")


def test_unknown_param():
    """Неизвестный параметр -- ошибка argparse."""
    with pytest.raises(SystemExit):
        parse_args(["--bad"])


def test_debug_output_lists_all_params(shell, recorder):
    """При запуске выводятся все параметры."""
    shell.start(Config("v.zip", None))
    text = recorder.text("debug")
    assert "vfs_path    = 'v.zip'" in text
    assert "script_path = None" in text


def test_comments_are_ignored():
    """Комментарий в стиле Python отбрасывается."""
    assert parse("ls /a  # комментарий") == ["ls", "/a"]
    assert parse("# только комментарий") == []


def test_hash_inside_word_or_quotes_is_kept():
    """Символ # внутри слова или кавычек -- обычный символ."""
    assert parse('ls a#b "#c"') == ["ls", "a#b", "#c"]


def test_script_echoes_input_and_output(shell, recorder, tmp_path):
    """Скрипт показывает приглашение с командой и её вывод."""
    script = tmp_path / "s.emu"
    script.write_text("# комментарий\n\nwho -q  # кто в системе\n",
                      encoding="utf-8")
    assert shell.run_script(str(script))
    assert ("echo", shell.prompt() + "# комментарий") in recorder.lines
    assert ("out", shell.user) in recorder.lines


def test_script_continues_after_error(shell, recorder, tmp_path):
    """После ошибки выполнение скрипта продолжается."""
    script = tmp_path / "s.emu"
    script.write_text("foo\nwho -q\n", encoding="utf-8")
    assert not shell.run_script(str(script))
    assert "команда не найдена" in recorder.text("err")
    assert "пользователей=1" in recorder.text("out")
    assert "строк с ошибками: 1" in recorder.text("debug")


def test_script_stops_on_exit(shell, recorder, tmp_path):
    """Команда exit в скрипте прекращает его выполнение."""
    script = tmp_path / "s.emu"
    script.write_text("exit\nfoo\n", encoding="utf-8")
    shell.run_script(str(script))
    assert "foo" not in recorder.text("err")


def test_missing_script(shell, recorder, tmp_path):
    """Несуществующий скрипт -- сообщение об ошибке."""
    assert not shell.run_script(str(tmp_path / "none.emu"))
    assert "не удалось прочитать скрипт" in recorder.text("err")

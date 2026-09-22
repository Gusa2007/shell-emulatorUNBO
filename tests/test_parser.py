"""Тесты парсера командной строки."""

import pytest

from emulator.parser import ParseError, parse


def test_empty_line():
    """Пустая строка и пробелы дают пустой список."""
    assert parse("") == []
    assert parse("   \t ") == []


def test_simple_words():
    """Слова разделяются любым количеством пробелов."""
    assert parse("ls  -l   /home") == ["ls", "-l", "/home"]


def test_double_quotes():
    """Двойные кавычки объединяют слова с пробелами."""
    assert parse('cd "My Documents"') == ["cd", "My Documents"]


def test_single_quotes_are_literal():
    """В одинарных кавычках обратная черта не экранирует."""
    assert parse(r"ls 'a\"b'") == ["ls", 'a\\"b']


def test_escapes_in_double_quotes():
    """Внутри "..." экранируются кавычка и обратная черта."""
    assert parse(r'ls "say \"hi\" \\ \n"') == ["ls", 'say "hi" \\ \\n']


def test_backslash_outside_quotes():
    """Вне кавычек обратная черта экранирует пробел."""
    assert parse(r"cd My\ Docs") == ["cd", "My Docs"]


def test_adjacent_parts_are_joined():
    """Соседние части в кавычках и без склеиваются в одно слово."""
    assert parse("a\"b c\"'d e'f") == ["ab cd ef"]


def test_empty_quoted_argument():
    """Пустые кавычки дают пустой аргумент."""
    assert parse('ls "" x') == ["ls", "", "x"]


@pytest.mark.parametrize("line", ['ls "abc', "ls 'abc", 'a "b\\"'])
def test_unclosed_quotes(line):
    """Незакрытая кавычка -- синтаксическая ошибка."""
    with pytest.raises(ParseError):
        parse(line)

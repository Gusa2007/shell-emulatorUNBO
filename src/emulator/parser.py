r"""Разбор командной строки на слова с учётом кавычек.

Правила повторяют поведение UNIX-оболочек:

* слова разделяются пробельными символами;
* внутри одинарных кавычек все символы берутся буквально;
* внутри двойных кавычек обратная косая черта экранирует
  символы ``"`` и ``\``;
* вне кавычек обратная косая черта экранирует следующий символ;
* соседние части слова склеиваются: ``a"b c"d`` -> ``ab cd``.
"""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, BACKSLASH)


class ParseError(Exception):
    """Ошибка синтаксиса командной строки (например, незакрытая кавычка)."""


class _Tokenizer:
    """Конечный автомат, превращающий строку в список слов."""

    def __init__(self, line):
        """Сохранить разбираемую строку и подготовить состояние."""
        self.line = line
        self.pos = 0
        self.words = []
        self.current = []
        self.in_word = False

    def run(self):
        """Разобрать всю строку и вернуть список слов."""
        while self.pos < len(self.line):
            char = self.line[self.pos]
            self.pos += 1
            self._consume(char)
        self._finish_word()
        return self.words

    def _consume(self, char):
        """Обработать очередной символ вне кавычек."""
        if char.isspace():
            self._finish_word()
        elif char == SINGLE_QUOTE:
            self._read_single_quoted()
        elif char == DOUBLE_QUOTE:
            self._read_double_quoted()
        elif char == BACKSLASH:
            self._append(self._take_escaped())
        else:
            self._append(char)

    def _append(self, text):
        """Добавить текст к текущему слову."""
        self.current.append(text)
        self.in_word = True

    def _finish_word(self):
        """Завершить текущее слово, если оно начато."""
        if self.in_word:
            self.words.append("".join(self.current))
        self.current = []
        self.in_word = False

    def _take_escaped(self):
        """Вернуть символ после обратной косой черты."""
        if self.pos >= len(self.line):
            return BACKSLASH
        char = self.line[self.pos]
        self.pos += 1
        return char

    def _read_single_quoted(self):
        """Прочитать содержимое одинарных кавычек буквально."""
        end = self.line.find(SINGLE_QUOTE, self.pos)
        if end < 0:
            raise ParseError("незакрытая одинарная кавычка")
        self._append(self.line[self.pos:end])
        self.pos = end + 1

    def _read_double_quoted(self):
        """Прочитать содержимое двойных кавычек с экранированием."""
        self.in_word = True
        while self.pos < len(self.line):
            char = self.line[self.pos]
            self.pos += 1
            if char == DOUBLE_QUOTE:
                return
            if char == BACKSLASH and self._next_is_escapable():
                char = self._take_escaped()
            self.current.append(char)
        raise ParseError("незакрытая двойная кавычка")

    def _next_is_escapable(self):
        r"""Проверить, экранирует ли ``\`` следующий символ в "..."."""
        return (self.pos < len(self.line)
                and self.line[self.pos] in ESCAPABLE_IN_DOUBLE)


def parse(line):
    """Разбить строку ``line`` на слова.

    Возвращает список строк. Пустая строка даёт пустой список.
    При синтаксической ошибке возбуждается :class:`ParseError`.
    """
    return _Tokenizer(line).run()

"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from emulator.shell import DEBUG, ECHO, ERR

FONT = ("Courier New", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
ERROR_COLOR = "#f48771"
PROMPT_COLOR = "#6a9955"
DEBUG_COLOR = "#808080"
START_DELAY_MS = 100
CLOSE_DELAY_MS = 300


class EmulatorApp:
    """Окно терминала: область вывода и строка ввода."""

    def __init__(self, shell, root=None):
        """Построить окно и подключить вывод оболочки к нему."""
        self.shell = shell
        self.root = root or tk.Tk()
        self.root.title(shell.title)
        self.root.geometry("820x520")
        shell.output = self.write
        self.input_history = []
        self.history_pos = 0
        self._build_output()
        self._build_input()

    def _build_output(self):
        """Создать область вывода только для чтения."""
        self.text = scrolledtext.ScrolledText(
            self.root, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, wrap=tk.WORD, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.tag_config(ERR, foreground=ERROR_COLOR)
        self.text.tag_config(ECHO, foreground=PROMPT_COLOR)
        self.text.tag_config(DEBUG, foreground=DEBUG_COLOR)

    def _build_input(self):
        """Создать строку ввода с приглашением."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X)
        self.prompt_label = tk.Label(
            frame, text=self.shell.prompt(), font=FONT,
            bg=BACKGROUND, fg=PROMPT_COLOR)
        self.prompt_label.pack(side=tk.LEFT)
        self.entry = tk.Entry(
            frame, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", lambda event: self._browse(-1))
        self.entry.bind("<Down>", lambda event: self._browse(1))
        self.entry.focus_set()

    def write(self, text, kind):
        """Добавить строку в область вывода."""
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, text + "\n", kind)
        self.text.configure(state=tk.DISABLED)
        self.text.see(tk.END)

    def start(self, config):
        """Запланировать стартовые действия после открытия окна."""
        self.root.after(START_DELAY_MS, self._start_now, config)

    def _start_now(self, config):
        """Выполнить стартовые действия оболочки."""
        self.shell.start(config)
        self._refresh()

    def submit(self, line):
        """Показать введённую строку и выполнить её."""
        self.write(self.shell.prompt() + line, ECHO)
        self.shell.execute(line)
        self._refresh()

    def _refresh(self):
        """Обновить приглашение и закрыть окно после exit."""
        self.prompt_label.configure(text=self.shell.prompt())
        if not self.shell.running:
            self.entry.configure(state=tk.DISABLED)
            self.root.after(CLOSE_DELAY_MS, self.root.destroy)

    def _on_enter(self, event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.input_history.append(line)
        self.history_pos = len(self.input_history)
        self.submit(line)

    def _browse(self, step):
        """Листать ранее введённые команды стрелками."""
        if not self.input_history:
            return
        last = len(self.input_history)
        self.history_pos = max(0, min(last, self.history_pos + step))
        self.entry.delete(0, tk.END)
        if self.history_pos < last:
            self.entry.insert(0, self.input_history[self.history_pos])

    def run(self):
        """Запустить главный цикл обработки событий."""
        self.root.mainloop()

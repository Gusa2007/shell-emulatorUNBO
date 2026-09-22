"""Тесты команд ls и cd (этап 4)."""


def out(recorder):
    """Вернуть строки обычного вывода."""
    return [text for kind, text in recorder.lines if kind == "out"]


def test_ls_root(vfs_shell, recorder):
    """Команда ls без аргументов выводит текущий каталог."""
    assert vfs_shell.execute("ls")
    assert out(recorder) == ["etc  home  motd  tmp"]


def test_ls_hidden_and_quoted(vfs_shell, recorder):
    """Скрытые файлы только с -a, имена с пробелами -- в кавычках."""
    vfs_shell.execute("ls /home/user")
    vfs_shell.execute("ls -a /home/user")
    assert out(recorder) == [
        "'My Documents'  docs",
        ".  ..  .profile  'My Documents'  docs",
    ]


def test_ls_long(vfs_shell, recorder):
    """Ключ -l даёт подробный вывод с правами и размером."""
    vfs_shell.execute("ls -l /etc")
    line = out(recorder)[0]
    assert line.startswith("-rw-r--r--  1 ")
    assert line.endswith(" hosts")
    assert " 19 " in line


def test_ls_combined_flags(vfs_shell, recorder):
    """Ключи можно объединять: -la."""
    assert vfs_shell.execute("ls -la /tmp")
    lines = out(recorder)
    assert lines[0].startswith("drwxr-xr-x") and lines[0].endswith(" .")
    assert lines[1].endswith(" ..")


def test_ls_file_and_several_dirs(vfs_shell, recorder):
    """Файл выводится по имени, каталоги -- с заголовками."""
    vfs_shell.execute("ls motd /etc /tmp")
    assert out(recorder) == ["motd", "", "/etc:", "hosts", "", "/tmp:"]


def test_ls_errors(vfs_shell, recorder):
    """Несуществующий путь и неверный ключ -- ошибки."""
    assert not vfs_shell.execute("ls /nope /etc")
    assert "невозможно получить доступ к '/nope'" in recorder.text("err")
    assert "hosts" in recorder.text("out")
    assert not vfs_shell.execute("ls -z")
    assert "ls: неверный ключ -- 'z'" in recorder.text("err")


def test_cd_absolute_relative_parent(vfs_shell):
    """Переходы по абсолютным, относительным путям и ..."""
    vfs_shell.execute("cd /home/user")
    vfs_shell.execute("cd docs/reports")
    assert vfs_shell.cwd == "/home/user/docs/reports"
    vfs_shell.execute("cd ../../..")
    assert vfs_shell.cwd == "/home"
    vfs_shell.execute('cd "user/My Documents"')
    assert vfs_shell.cwd == "/home/user/My Documents"
    assert vfs_shell.prompt().endswith(":/home/user/My Documents$ ")


def test_cd_home_and_previous(vfs_shell, recorder):
    """Без аргументов и с ~ -- в корень, с - -- в предыдущий каталог."""
    vfs_shell.execute("cd /etc")
    vfs_shell.execute("cd")
    assert vfs_shell.cwd == "/"
    vfs_shell.execute("cd -")
    assert vfs_shell.cwd == "/etc"
    assert out(recorder) == ["/etc"]
    vfs_shell.execute("cd ~")
    assert vfs_shell.cwd == "/"


def test_ls_uses_cwd(vfs_shell, recorder):
    """Относительные пути ls считаются от текущего каталога."""
    vfs_shell.execute("cd /home/user")
    vfs_shell.execute("ls docs")
    assert out(recorder) == ["empty  reports"]


def test_cd_errors(vfs_shell, recorder):
    """Ошибки cd не меняют текущий каталог."""
    vfs_shell.execute("cd /etc")
    assert not vfs_shell.execute("cd /nope")
    assert not vfs_shell.execute("cd hosts")
    assert not vfs_shell.execute("cd a b")
    assert vfs_shell.cwd == "/etc"
    errors = recorder.text("err")
    assert "cd: /nope: Нет такого файла или каталога" in errors
    assert "cd: hosts: Это не каталог" in errors
    assert "cd: слишком много аргументов" in errors


def test_cd_previous_not_set(shell, recorder):
    """Команда cd - без предыдущего каталога -- ошибка."""
    assert not shell.execute("cd -")
    assert "OLDPWD не задан" in recorder.text("err")

"""Команды работы с VFS: ls, cd."""

from emulator.commands.registry import CommandError, command, parse_flags
from emulator.vfs import CURRENT, PARENT, VFSError

HOME = "/"
PREVIOUS_DIR = "-"
TILDE = "~"
MAX_CD_ARGS = 1
SINGLE_OPERAND = 1
DIR_SIZE = 4096
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
BASE_DIR_LINKS = 2
FILE_LINKS = 1
TIME_FORMAT = "%b %d %H:%M"
SIZE_WIDTH = 6
LINKS_WIDTH = 2
HIDDEN_PREFIX = "."


def quote_name(name):
    """Взять имя в кавычки, если в нём есть пробелы (как GNU ls)."""
    if " " in name or not name:
        return f"'{name}'"
    return name


def link_count(node):
    """Число жёстких ссылок: для каталога 2 + число подкаталогов."""
    if not node.is_dir:
        return FILE_LINKS
    subdirs = sum(1 for child in node.children.values() if child.is_dir)
    return BASE_DIR_LINKS + subdirs


def long_entry(shell, node, name):
    """Строка подробного вывода ``ls -l`` для узла ``node``."""
    mode = DIR_MODE if node.is_dir else FILE_MODE
    size = DIR_SIZE if node.is_dir else node.size
    links = link_count(node)
    stamp = node.mtime.strftime(TIME_FORMAT)
    return (f"{mode} {links:>{LINKS_WIDTH}} {shell.user} {shell.user} "
            f"{size:>{SIZE_WIDTH}} {stamp} {quote_name(name)}")


def dir_entries(directory, show_all):
    """Вернуть список пар (имя, узел) содержимого каталога."""
    entries = []
    if show_all:
        parent = directory.parent or directory
        entries = [(CURRENT, directory), (PARENT, parent)]
    for name in sorted(directory.children):
        if show_all or not name.startswith(HIDDEN_PREFIX):
            entries.append((name, directory.children[name]))
    return entries


def print_entries(shell, entries, flags):
    """Вывести список пар (имя, узел) в кратком или подробном виде."""
    if "l" in flags:
        for name, node in entries:
            shell.write(long_entry(shell, node, name))
    elif entries:
        shell.write("  ".join(quote_name(name) for name, _ in entries))


def resolve_all(shell, paths):
    """Разрешить пути; вернуть (файлы, каталоги, были ли ошибки)."""
    files, dirs, ok = [], [], True
    for path in paths:
        try:
            node = shell.vfs.lookup(path, shell.cwd)
        except VFSError as exc:
            shell.error(f"ls: невозможно получить доступ к '{path}': {exc}")
            ok = False
            continue
        (dirs if node.is_dir else files).append((path, node))
    return files, dirs, ok


@command("ls", "вывести содержимое каталога", "ls [-l] [-a] [путь...]")
def cmd_ls(shell, args):
    """Вывести содержимое каталогов; -l -- подробно, -a -- все файлы."""
    flags, paths = parse_flags(args, "la")
    files, dirs, ok = resolve_all(shell, paths or [CURRENT])
    print_entries(shell, files, flags)
    with_titles = len(paths) > SINGLE_OPERAND
    for index, (path, node) in enumerate(dirs):
        if files or index:
            shell.write("")
        if with_titles:
            shell.write(f"{path}:")
        print_entries(shell, dir_entries(node, "a" in flags), flags)
    return ok


def cd_target(shell, args):
    """Определить путь, в который нужно перейти."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("слишком много аргументов")
    if not args or args[0] == TILDE:
        return HOME
    if args[0] == PREVIOUS_DIR:
        if shell.oldpwd is None:
            raise CommandError("OLDPWD не задан")
        shell.write(shell.oldpwd)
        return shell.oldpwd
    return args[0]


@command("cd", "сменить текущий каталог", "cd [путь | - | ~]")
def cmd_cd(shell, args):
    """Сменить текущий каталог; без аргументов -- домашний (/)."""
    target = cd_target(shell, args)
    try:
        node = shell.vfs.lookup(target, shell.cwd)
    except VFSError as exc:
        raise CommandError(f"{target}: {exc}") from exc
    if not node.is_dir:
        raise CommandError(f"{target}: Это не каталог")
    shell.oldpwd = shell.cwd
    shell.cwd = node.path

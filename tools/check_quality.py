"""Строгая проверка ограничений оформления из задания."""

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_LINES = 1000
MAX_PYTHON_WIDTH = 80
MAX_TEXT_WIDTH = 120
MAX_FUNCTION_LINES = 40
MAX_ARGUMENTS = 7
MAX_COMPLEXITY = 10
ZERO = 0
REQUIRED = ("README.md", ".gitignore", "src", "tests", "run.bat")
FORBIDDEN_PARTS = {
    ".idea", ".vscode", ".venv", "__pycache__", "build", "dist",
}
FORBIDDEN_SUFFIXES = {
    ".bin", ".pyc", ".pyo", ".zip", ".gz", ".tar", ".pdf",
    ".png", ".jpg", ".exe", ".dll", ".so", ".whl",
}
DECISIONS = (
    ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler,
    ast.comprehension, ast.Assert, ast.Match,
)


def git_output(*arguments: str) -> str:
    """Получить текст Git без вывода секретов или параметров окружения."""
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True, encoding="utf-8",
    )


def tracked_paths() -> list[Path]:
    """Проверять только файлы, включённые в индекс Git."""
    return [ROOT / name for name in git_output("ls-files").splitlines()]


def function_complexity(node: ast.AST) -> int:
    """Учесть все ветвления, циклы, генераторы и логические операторы."""
    complexity = 1
    for child in ast.walk(node):
        complexity += isinstance(child, DECISIONS)
        if isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        if isinstance(child, ast.comprehension):
            complexity += len(child.ifs)
        if isinstance(child, ast.Match):
            complexity += len(child.cases)
    return complexity


def argument_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Посчитать также self, позиционные и именованные аргументы."""
    args = node.args
    return (len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs)
            + bool(args.vararg) + bool(args.kwarg))


def check_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Считать длину от def до последней строки, включая документацию."""
    errors = []
    size = node.end_lineno - node.lineno + 1
    if size > MAX_FUNCTION_LINES:
        errors.append(f"{node.name}: длина {size} > {MAX_FUNCTION_LINES}")
    if argument_count(node) > MAX_ARGUMENTS:
        errors.append(f"{node.name}: слишком много аргументов")
    complexity = function_complexity(node)
    if complexity > MAX_COMPLEXITY:
        errors.append(f"{node.name}: сложность {complexity}")
    return errors


def is_number(node: ast.AST) -> bool:
    """Распознать числовой литерал, в том числе с унарным знаком."""
    if isinstance(node, ast.UnaryOp):
        return is_number(node.operand)
    return (isinstance(node, ast.Constant)
            and type(node.value) in (int, float, complex))


def check_node(node: ast.AST) -> list[str]:
    """Проверить функции, docstring и отсутствие чисел в сравнениях."""
    errors = []
    documented = (ast.Module, ast.ClassDef, ast.FunctionDef,
                  ast.AsyncFunctionDef)
    if isinstance(node, documented) and ast.get_docstring(node) is None:
        errors.append(f"Нет docstring: {getattr(node, 'name', 'module')}")
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        errors.extend(check_function(node))
    if isinstance(node, ast.Compare):
        if any(is_number(item) for item in [node.left, *node.comparators]):
            errors.append(f"Строка {node.lineno}: число в сравнении")
    return errors


def check_text(content: str, suffix: str) -> list[str]:
    """Проверить размеры текстового файла и дерево Python."""
    lines = content.splitlines()
    width = MAX_PYTHON_WIDTH if suffix == ".py" else MAX_TEXT_WIDTH
    errors = [f"Строка {index}: длина {len(line)} > {width}"
              for index, line in enumerate(lines, 1) if len(line) > width]
    if len(lines) > MAX_FILE_LINES:
        errors.append(f"Файл содержит больше {MAX_FILE_LINES} строк")
    if "\x00" in content:
        errors.append("Бинарные данные в текстовом файле")
    if suffix == ".py":
        for node in ast.walk(ast.parse(content)):
            errors.extend(check_node(node))
    return errors


def check_file(path: Path) -> list[str]:
    """Проверить тип файла и добавить имя к сообщениям анализа текста."""
    relative = path.relative_to(ROOT)
    if set(relative.parts) & FORBIDDEN_PARTS:
        return [f"Служебный каталог: {relative}"]
    if path.suffix in FORBIDDEN_SUFFIXES:
        return [f"Запрещённый тип: {relative}"]
    content = path.read_text(encoding="utf-8")
    errors = check_text(content, path.suffix)
    return [f"{relative}: {error}" for error in errors]


def check_commits() -> list[str]:
    """Проверить Conventional/Scoped Commits и наличие подробного тела."""
    if not git_output("rev-parse", "--verify", "--quiet", "HEAD").strip():
        return []
    errors = []
    pattern = r"^(feat|fix|test|docs|chore|refactor)\([a-z0-9_-]+\): .+"
    records = git_output("log", "--format=%s%x1f%b%x1e").split("\x1e")
    for record in records:
        if not record.strip():
            continue
        subject, body = record.strip().split("\x1f", maxsplit=1)
        if not re.fullmatch(pattern, subject) or not body.strip():
            errors.append(f"Недостаточно оформлен коммит: {subject}")
    return errors


def main() -> int:
    """Проверить индекс Git и завершиться с ошибкой при нарушении."""
    errors = [f"Отсутствует {name}" for name in REQUIRED
              if not (ROOT / name).exists()]
    paths = tracked_paths()
    for path in paths:
        errors.extend(check_file(path))
    try:
        errors.extend(check_commits())
    except subprocess.CalledProcessError:
        pass
    for error in errors:
        print(error)
    print(f"Проверено файлов: {len(paths)}; нарушений: {len(errors)}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

"""Аргументы командной строки и сообщения об ошибках."""

import argparse
import sys
from pathlib import Path

from src.assembler import assemble

SUCCESS = 0
FAILURE = 1


def build_parser() -> argparse.ArgumentParser:
    """Создать CLI с подкомандой assemble."""
    parser = argparse.ArgumentParser(description="УВМ, вариант 1")
    commands = parser.add_subparsers(dest="command", required=True)
    assembler = commands.add_parser("assemble", help="Ассемблировать программу")
    assembler.add_argument("source", type=Path, help="Файл программы UTF-8")
    assembler.add_argument("output", type=Path, help="Двоичный файл результата")
    assembler.add_argument("--test", action="store_true", help="Тестовый вывод")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Выполнить команду и вернуть ненулевой код при ошибке."""
    arguments = build_parser().parse_args(argv)
    try:
        assemble(arguments.source, arguments.output, arguments.test)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return FAILURE
    return SUCCESS

"""Аргументы командной строки и сообщения об ошибках."""

import argparse
import sys
from pathlib import Path

from src.assembler import assemble
from src.interpreter import interpret
from src.parser import parse_integer

SUCCESS = 0
FAILURE = 1


def build_parser() -> argparse.ArgumentParser:
    """Создать CLI с подкомандами assemble и run."""
    parser = argparse.ArgumentParser(description="УВМ, вариант 1")
    commands = parser.add_subparsers(dest="command", required=True)
    assembler = commands.add_parser("assemble", help="Ассемблировать программу")
    assembler.add_argument("source", type=Path, help="Файл программы UTF-8")
    assembler.add_argument("output", type=Path, help="Двоичный файл результата")
    assembler.add_argument("--test", action="store_true", help="Тестовый вывод")
    interpreter = commands.add_parser("run", help="Выполнить программу УВМ")
    interpreter.add_argument("program", type=Path, help="Двоичный файл")
    interpreter.add_argument("output", type=Path, help="XML-дамп памяти")
    interpreter.add_argument("--start", type=parse_integer, required=True,
                             help="Первый адрес дампа включительно")
    interpreter.add_argument("--end", type=parse_integer, required=True,
                             help="Последний адрес дампа включительно")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Выполнить команду и вернуть ненулевой код при ошибке."""
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "assemble":
            assemble(arguments.source, arguments.output, arguments.test)
        else:
            interpret(arguments.program, arguments.output,
                      arguments.start, arguments.end)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return FAILURE
    return SUCCESS

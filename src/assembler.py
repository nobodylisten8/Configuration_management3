"""Трансляция текстовой программы в промежуточное представление."""

from pathlib import Path

from src.parser import parse_program


def assemble(source: Path, output: Path, test_mode: bool = False) -> None:
    """Прочитать исходник; на этапе 1 двоичный файл ещё не создаётся."""
    instructions = parse_program(source.read_text(encoding="utf-8-sig"))
    if test_mode:
        for instruction in instructions:
            print(instruction.fields())
    print(f"Разобрано команд: {len(instructions)}; результат: {output}")

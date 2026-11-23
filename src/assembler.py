"""Трансляция исходника через IR в двоичный машинный код."""

from pathlib import Path

from src.codec import encode_instruction, encode_program, format_bytes
from src.parser import parse_program


def assemble(source: Path, output: Path, test_mode: bool = False) -> None:
    """Записать бинарный результат и вывести размер и тестовые байты."""
    if source.resolve() == output.resolve():
        raise ValueError("Исходный и выходной файлы должны различаться")
    instructions = parse_program(source.read_text(encoding="utf-8-sig"))
    data = encode_program(instructions)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    if test_mode:
        for instruction in instructions:
            print(format_bytes(encode_instruction(instruction)))
    print(f"Размер двоичного файла: {len(data)} байт")

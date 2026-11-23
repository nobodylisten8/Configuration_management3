"""Тесты промежуточного представления и диагностики ассемблера."""

import unittest
from pathlib import Path

from src.isa import CONSTANT_MAX, CONSTANT_MIN
from src.parser import parse_program

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FIELDS = [
    {"A": 26, "B": 28, "C": 43},
    {"A": 46, "B": 9, "C": 55},
    {"A": 49, "B": 127, "C": 271, "D": 20},
    {"A": 59, "B": 23, "C": 65},
]


class ParserTests(unittest.TestCase):
    """Проверки всех команд, границ полей и ошибочных исходников."""

    def test_specification_fields(self):
        """Воспроизвести все поля из примеров задания."""
        source = (ROOT / "examples/specification.asm").read_text("utf-8")
        result = [item.fields() for item in parse_program(source)]
        self.assertEqual(result, EXPECTED_FIELDS)

    def test_comments_case_and_bases(self):
        """Принять комментарии, регистр мнемоник и основания чисел."""
        result = parse_program("; comment\nload 0x1c, 0b101011 ; value\n")
        self.assertEqual(result[0].fields(), EXPECTED_FIELDS[0])

    def test_signed_boundaries(self):
        """Принять крайние представимые знаковые константы."""
        for value in (CONSTANT_MIN, CONSTANT_MAX):
            with self.subTest(value=value):
                instruction = parse_program(f"LOAD 127, {value}")[0]
                self.assertEqual(instruction.operands, (127, value))

    def test_invalid_programs(self):
        """Отклонить неверные поля, числа, команды и количество аргументов."""
        sources = (
            "BAD 1, 2", "LOAD", "LOAD 0, 1, 2", "LOAD 128, 1",
            "LOAD -1, 1", "READ 0, 128", "STORE 0, 32768, 0",
            "STORE 0, -1, 0", "STORE 0, 0, 128", "ABS 0, 128",
            "LOAD 0, text", "LOAD 0 1", "LOAD 0,", "READ 0,,1",
            f"LOAD 0, {CONSTANT_MAX + 1}",
            f"LOAD 0, {CONSTANT_MIN - 1}",
        )
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "Строка 2:"):
                    parse_program("; first line\n" + source)

    def test_empty_program(self):
        """Пустая программа содержит ноль инструкций."""
        self.assertEqual(parse_program("\n; empty\n"), [])

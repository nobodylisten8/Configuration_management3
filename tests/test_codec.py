"""Проверки двоичного формата на независимых эталонах из задания."""

import unittest
from pathlib import Path

from src.codec import decode_instruction, encode_instruction, encode_program
from src.isa import CONSTANT_MAX, CONSTANT_MIN, INSTRUCTION_BYTES
from src.parser import parse_program

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEX = (
    "1A 67 05 00 00 00",
    "6E E2 06 00 00 00",
    "F1 FF 21 40 01 00",
    "FB 25 08 00 00 00",
)


class CodecTests(unittest.TestCase):
    """Байты, обратное преобразование, знаковость и испорченный код."""

    def test_specification_bytes(self):
        """Сравнить все четыре команды с точными шестибайтовыми эталонами."""
        text = (ROOT / "examples/specification.asm").read_text("utf-8")
        program = parse_program(text)
        expected = b"".join(bytes.fromhex(item) for item in EXPECTED_HEX)
        self.assertEqual(encode_program(program), expected)
        for instruction, hex_text in zip(program, EXPECTED_HEX):
            with self.subTest(command=instruction.operation.name):
                self.assertEqual(encode_instruction(instruction),
                                 bytes.fromhex(hex_text))
                self.assertEqual(decode_instruction(bytes.fromhex(hex_text)),
                                 instruction)

    def test_field_boundaries_roundtrip(self):
        """Проверить крайние адреса, смещения и отрицательные константы."""
        text = (f"LOAD 0, {CONSTANT_MIN}\nLOAD 127, {CONSTANT_MAX}\n"
                "LOAD 0, -1\nREAD 127, 127\nSTORE 127, 32767, 127\n"
                "ABS 127, 127")
        for instruction in parse_program(text):
            with self.subTest(instruction=instruction):
                self.assertEqual(
                    decode_instruction(encode_instruction(instruction)),
                    instruction,
                )

    def test_invalid_binary(self):
        """Отклонить обрезанные команды, неверный opcode и резервные биты."""
        samples = (b"", b"\x1a", bytes(INSTRUCTION_BYTES),
                   bytes.fromhex("1A 00 00 00 00 80"),
                   bytes.fromhex("2E 00 10 00 00 00"),
                   bytes.fromhex("31 00 00 00 08 00"))
        for data in samples:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    decode_instruction(data)

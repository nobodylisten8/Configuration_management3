"""Проверки унарной операции abs() с записью по косвенному адресу."""

import unittest
from pathlib import Path

from src.isa import CONSTANT_MIN
from src.machine import MEMORY_SIZE
from tests.test_machine import execute_text

ROOT = Path(__file__).resolve().parents[1]


class AluTests(unittest.TestCase):
    """Проверки знака, адресации и сохранности регистров."""

    def test_scalar_program(self):
        """Выполнить пример для отрицательного, нулевого и положительного."""
        source = (ROOT / "examples/abs_scalar.asm").read_text("utf-8")
        machine = execute_text(source)
        self.assertEqual(machine.memory[1200:1203], [13, 0, 21])

    def test_minimum_constant_and_registers(self):
        """Модуль минимальной константы не переполняется и не меняет R."""
        machine = execute_text(f"LOAD 23, {CONSTANT_MIN}\n"
                               "LOAD 65, 1500\nABS 23, 65")
        self.assertEqual(machine.read_memory(1500), -CONSTANT_MIN)
        self.assertEqual(machine.registers[23], CONSTANT_MIN)
        self.assertEqual(machine.registers[65], 1500)

    def test_same_source_and_pointer(self):
        """B и C могут обозначать один и тот же регистр."""
        machine = execute_text("LOAD 5, 1500\nABS 5, 5")
        self.assertEqual(machine.read_memory(1500), 1500)

    def test_invalid_destination(self):
        """Проверять границы адреса назначения abs(), включая отрицательные."""
        for address in (-1, MEMORY_SIZE):
            with self.subTest(address=address):
                with self.assertRaisesRegex(ValueError, "PC=12"):
                    execute_text(f"LOAD 0, -9\nLOAD 1, {address}\nABS 0, 1")

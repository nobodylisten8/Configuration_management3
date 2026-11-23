"""Проверки исполнения и единой памяти команд и данных."""

import unittest
from pathlib import Path

from src.codec import encode_program
from src.machine import MEMORY_SIZE, Machine
from src.parser import parse_program

ROOT = Path(__file__).resolve().parents[1]


def execute_text(source: str) -> Machine:
    """Выполнить тестовый исходник через настоящий машинный код."""
    machine = Machine(encode_program(parse_program(source)))
    machine.run()
    return machine


class MachineTests(unittest.TestCase):
    """Копирование массива, косвенная адресация и границы памяти."""

    def test_copy_array(self):
        """Скопировать четыре ячейки и сохранить исходный массив."""
        source = (ROOT / "examples/copy_array.asm").read_text("utf-8")
        machine = execute_text(source)
        self.assertEqual(machine.memory[1000:1004], [5, -7, 0, 42])
        self.assertEqual(machine.memory[1100:1104], [5, -7, 0, 42])

    def test_shared_code_and_data_memory(self):
        """STORE изменяет будущую инструкцию, fetch читает новые байты."""
        machine = execute_text("LOAD 0, 26\nLOAD 1, 18\n"
                               "STORE 0, 0, 1\nREAD 0, 2")
        self.assertEqual(machine.memory[18], 26)
        self.assertEqual(machine.registers[0], 2)

    def test_read_code_as_data(self):
        """Команда READ может прочитать первый байт собственного кода."""
        machine = execute_text("LOAD 0, 0\nREAD 0, 1")
        self.assertEqual(machine.registers[1], 26)

    def test_memory_boundaries(self):
        """Прочитать и записать первую и последнюю ячейки памяти."""
        machine = Machine(b"")
        for address in (0, MEMORY_SIZE - 1):
            machine.write_memory(address, -123)
            self.assertEqual(machine.read_memory(address), -123)

    def test_invalid_addresses(self):
        """Отклонить выход за память для READ и STORE со смещением."""
        sources = ("LOAD 0, -1\nREAD 0, 1",
                   f"LOAD 0, {MEMORY_SIZE}\nREAD 0, 1",
                   f"LOAD 0, {MEMORY_SIZE - 1}\nSTORE 1, 1, 0")
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "PC="):
                    execute_text(source)

    def test_invalid_program_size(self):
        """Отклонить обрезанную программу и переполнение общей памяти."""
        for program, size in ((b"\x1a", MEMORY_SIZE), (bytes(12), 6)):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    Machine(program, size)

    def test_invalid_code_in_shared_memory(self):
        """Диагностировать запись значения вне байта в следующую команду."""
        source = "LOAD 0, -1\nLOAD 1, 18\nSTORE 0, 0, 1\nLOAD 0, 0"
        with self.assertRaisesRegex(ValueError, "PC=18"):
            execute_text(source)

"""Проверки XML-дампа и CLI интерпретатора."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from xml.etree.ElementTree import parse

from src.cli import FAILURE, SUCCESS, main
from src.interpreter import dump_memory
from src.machine import MEMORY_SIZE, Machine

ROOT = Path(__file__).resolve().parents[1]


class InterpreterTests(unittest.TestCase):
    """Границы диапазона, XML и ошибки выполнения."""

    def test_cli_copy_dump(self):
        """Собрать и выполнить копирование, прочитать полученный XML."""
        with tempfile.TemporaryDirectory() as directory:
            binary = str(Path(directory) / "copy.bin")
            output = str(Path(directory) / "copy.xml")
            with contextlib.redirect_stdout(io.StringIO()):
                status = main(["assemble", str(ROOT / "examples" /
                               "copy_array.asm"), binary])
                self.assertEqual(status, SUCCESS)
                status = main(["run", binary, output, "--start", "1100",
                               "--end", "1103"])
            self.assertEqual(status, SUCCESS)
            root = parse(output).getroot()
            self.assertEqual(root.attrib, {"start": "1100", "end": "1103"})
            self.assertEqual([int(cell.text) for cell in root], [5, -7, 0, 42])
            self.assertEqual([cell.get("address") for cell in root],
                             ["1100", "1101", "1102", "1103"])

    def test_single_cell_dump(self):
        """Обе границы включительны, допускается диапазон из одной ячейки."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "single.xml"
            machine = Machine(b"")
            machine.write_memory(0, -7)
            dump_memory(machine, output, 0, 0)
            root = parse(output).getroot()
            self.assertEqual([(cell.get("address"), cell.text)
                              for cell in root], [("0", "-7")])

    def test_invalid_ranges(self):
        """Отклонить обратный диапазон и адреса за границами."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "invalid.xml"
            for start, end in ((5, 4), (-1, 1), (0, MEMORY_SIZE)):
                with self.subTest(start=start, end=end):
                    with self.assertRaises(ValueError):
                        dump_memory(Machine(b""), output, start, end)
            self.assertFalse(output.exists())

    def test_runtime_failure_preserves_dump(self):
        """Ошибочная программа возвращает код 1 и не меняет старый дамп."""
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "bad.bin"
            output = Path(directory) / "old.xml"
            binary.write_bytes(bytes(6))
            output.write_text("previous", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = main(["run", str(binary), str(output),
                               "--start", "0", "--end", "0"])
            self.assertEqual(status, FAILURE)
            self.assertIn("PC=0", stderr.getvalue())
            self.assertEqual(output.read_text("utf-8"), "previous")

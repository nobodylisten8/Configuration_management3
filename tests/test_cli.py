"""Интеграционные проверки CLI с реальными временными файлами."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.cli import FAILURE, SUCCESS, main
from tests.test_codec import EXPECTED_HEX

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Выходные файлы, тестовый вывод и обработка ошибок."""

    def test_assemble_file(self):
        """Сохранить ровно 24 эталонных байта и вывести их размер."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested/program.bin"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = main(["assemble", str(ROOT / "examples" /
                               "specification.asm"), str(output), "--test"])
            expected = b"".join(bytes.fromhex(item) for item in EXPECTED_HEX)
            self.assertEqual(status, SUCCESS)
            self.assertEqual(output.read_bytes(), expected)
            self.assertIn("24 байт", stdout.getvalue())
            self.assertIn("0x1A, 0x67, 0x05", stdout.getvalue())

    def test_failed_assembly_preserves_output(self):
        """Ошибка разбора не должна уничтожать существующий результат."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.asm"
            output = Path(directory) / "program.bin"
            source.write_text("BAD 0, 0", encoding="utf-8")
            output.write_bytes(b"previous")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = main(["assemble", str(source), str(output)])
            self.assertEqual(status, FAILURE)
            self.assertEqual(output.read_bytes(), b"previous")
            self.assertIn("Строка 1", stderr.getvalue())

    def test_missing_source(self):
        """Отсутствующий файл выдаёт понятную ошибку без traceback."""
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.asm"
            with contextlib.redirect_stderr(io.StringIO()):
                status = main(["assemble", str(missing), str(missing) + ".bin"])
            self.assertEqual(status, FAILURE)

    def test_same_source_and_output(self):
        """Запретить перезапись исходника двоичным файлом."""
        path = str(ROOT / "examples/specification.asm")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["assemble", path, path]), FAILURE)

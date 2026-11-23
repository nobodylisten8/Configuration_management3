"""Сквозная проверка всех программ, включая три вектора длины восемь."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.demo import ROOT, load_cases, run_case, verify_xml

VECTOR_LENGTH = 8
SUCCESS = 0


class ExampleTests(unittest.TestCase):
    """Сборка, исполнение, сохранность входа и содержимое дампов."""

    def test_all_examples(self):
        """Проверить все примеры по независимым ожидаемым значениям."""
        with tempfile.TemporaryDirectory() as directory:
            for case in load_cases():
                with self.subTest(program=case["name"]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        dump = run_case(case, Path(directory))
                    reference = ROOT / "examples/expected" / dump.name
                    verify_xml(reference, case["start"], case["expected"])

    def test_three_vector_cases(self):
        """Каждый из трёх вариантов содержит ровно восемь входов и выходов."""
        cases = [case for case in load_cases()
                 if case["name"].startswith("vector_")]
        self.assertEqual({case["name"] for case in cases},
                         {"vector_mixed", "vector_negative",
                          "vector_boundaries"})
        for case in cases:
            self.assertEqual(len(case["source"]), VECTOR_LENGTH)
            self.assertEqual(len(case["expected"]), VECTOR_LENGTH)
            self.assertNotEqual(case["source_start"], case["start"])

    def test_real_python_entrypoint(self):
        """Выполнить сборку и интерпретацию отдельными процессами Python."""
        case = next(item for item in load_cases()
                    if item["name"] == "vector_mixed")
        with tempfile.TemporaryDirectory() as directory:
            binary = str(Path(directory) / "program.bin")
            dump = Path(directory) / "dump.xml"
            source = str(ROOT / "examples/vector_mixed.asm")
            commands = (["assemble", source, binary, "--test"],
                        ["run", binary, str(dump), "--start", "1100",
                         "--end", "1107"])
            for arguments in commands:
                result = subprocess.run(
                    [sys.executable, "-m", "src", *arguments], cwd=ROOT,
                    capture_output=True, text=True, encoding="utf-8",
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                    check=False,
                )
                self.assertEqual(result.returncode, SUCCESS, result.stderr)
            verify_xml(dump, case["start"], case["expected"])

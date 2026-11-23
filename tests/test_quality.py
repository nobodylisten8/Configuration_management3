"""Регрессии строгого подсчёта длины, сложности и магических сравнений."""

import ast
import unittest

from tools.check_quality import (
    MAX_FUNCTION_LINES,
    check_function,
    check_node,
    function_complexity,
)


class QualityTests(unittest.TestCase):
    """Не допускать ослабления проверок из-за docstring и вложенных if."""

    def test_docstring_counts_towards_function_length(self):
        """Многострочный docstring входит в длину от def до конца функции."""
        lines = MAX_FUNCTION_LINES - 2
        source = 'def sample():\n    """\n' + '    text\n' * lines
        source += '    """\n    return None\n'
        function = ast.parse(source).body[0]
        self.assertTrue(check_function(function))

    def test_nested_decisions_are_counted(self):
        """Вложенный цикл, if и логические операторы повышают сложность."""
        source = ("def sample(values):\n"
                  "    for item in values:\n"
                  "        if item and values:\n"
                  "            if values:\n"
                  "                return item\n")
        self.assertEqual(function_complexity(ast.parse(source).body[0]), 5)

    def test_magic_comparison_literals(self):
        """Проверить положительные, отрицательные и цепочные литералы."""
        for expression in ("x < 8", "x >= -1", "0 <= x < limit"):
            comparison = ast.parse(expression).body[0].value
            self.assertTrue(check_node(comparison))
        comparison = ast.parse("ZERO <= x < LIMIT").body[0].value
        self.assertEqual(check_node(comparison), [])

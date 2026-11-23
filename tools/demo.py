"""Сборка и исполнение всех примеров с проверкой XML и исходных данных."""

import json
from pathlib import Path
from xml.etree.ElementTree import parse

from src.assembler import assemble
from src.interpreter import interpret

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def load_cases() -> list[dict]:
    """Прочитать независимые входные данные и эталоны примеров."""
    path = ROOT / "examples/cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


def verify_xml(path: Path, start: int, expected: list[int]) -> None:
    """Проверить корень, диапазон, адреса и значения XML-дампа."""
    root = parse(path).getroot()
    end = start + len(expected) - 1
    attributes = {"start": str(start), "end": str(end)}
    if root.tag != "memory" or root.attrib != attributes:
        raise ValueError(f"Неверный диапазон XML: {path}")
    actual = [(cell.get("address"), cell.text) for cell in root]
    wanted = [(str(start + index), str(value))
              for index, value in enumerate(expected)]
    if actual != wanted:
        raise ValueError(f"Неверные адреса или значения XML: {path}")


def run_case(case: dict, output_directory: Path) -> Path:
    """Собрать, выполнить и проверить один пример, вернуть путь к дампу."""
    name = case["name"]
    source = ROOT / "examples" / f"{name}.asm"
    binary = output_directory / f"{name}.bin"
    dump = output_directory / f"{name}.xml"
    start = case["start"]
    end = start + len(case["expected"]) - 1
    assemble(source, binary)
    machine = interpret(binary, dump, start, end)
    verify_xml(dump, start, case["expected"])
    source_start = case["source_start"]
    if source_start is not None:
        source_end = source_start + len(case["source"])
        if machine.memory[source_start:source_end] != case["source"]:
            raise ValueError(f"Исходный массив изменён: {name}")
    return dump


def main() -> None:
    """Создать локальные результаты; двоичные файлы не включаются в Git."""
    for case in load_cases():
        run_case(case, OUTPUT)
        print(f"OK {case['name']}: {case['expected']}")


if __name__ == "__main__":
    main()

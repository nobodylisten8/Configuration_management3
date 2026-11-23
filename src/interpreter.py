"""Запуск двоичной программы и сохранение диапазона общей памяти в XML."""

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

from src.isa import INSTRUCTION_BYTES
from src.machine import Machine


def validate_range(machine: Machine, start: int, end: int) -> None:
    """Проверить включительные границы диапазона дампа."""
    machine.check_address(start)
    machine.check_address(end)
    if start > end:
        raise ValueError("Начало диапазона больше конца")


def dump_memory(machine: Machine, output: Path, start: int, end: int) -> None:
    """Записать XML с адресами и значениями ячеек, включая обе границы."""
    validate_range(machine, start, end)
    root = Element("memory", start=str(start), end=str(end))
    for address in range(start, end + 1):
        cell = SubElement(root, "cell", address=str(address))
        cell.text = str(machine.read_memory(address))
    indent(root, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    ElementTree(root).write(
        output, encoding="utf-8", xml_declaration=True,
    )


def interpret(program: Path, output: Path, start: int, end: int) -> Machine:
    """Загрузить, выполнить программу и сохранить дамп после успеха."""
    if program.resolve() == output.resolve():
        raise ValueError("Двоичный файл и дамп должны различаться")
    machine = Machine(program.read_bytes())
    validate_range(machine, start, end)
    machine.run()
    dump_memory(machine, output, start, end)
    count = machine.pc // INSTRUCTION_BYTES
    print(f"Выполнено команд: {count}; дамп: {output}")
    return machine

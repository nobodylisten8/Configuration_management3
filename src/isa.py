"""Описание полей шестибайтовых инструкций варианта 1."""

from dataclasses import dataclass

INSTRUCTION_BYTES = 6
REGISTER_COUNT = 128
CONSTANT_BITS = 27
CONSTANT_MIN = -(1 << (CONSTANT_BITS - 1))
CONSTANT_MAX = (1 << (CONSTANT_BITS - 1)) - 1
OFFSET_MAX = (1 << 15) - 1
ZERO = 0


@dataclass(frozen=True)
class Operation:
    """Мнемоника, код операции и ширины полей после A."""

    name: str
    opcode: int
    widths: tuple[int, ...]


OPERATIONS = {
    "LOAD": Operation("LOAD", 26, (7, 27)),
    "READ": Operation("READ", 46, (7, 7)),
    "STORE": Operation("STORE", 49, (7, 15, 7)),
    "ABS": Operation("ABS", 59, (7, 7)),
}
OPCODE_BITS = 6
FIELD_NAMES = ("B", "C", "D")


@dataclass(frozen=True)
class Instruction:
    """Проверенная инструкция в промежуточном представлении."""

    operation: Operation
    operands: tuple[int, ...]

    def fields(self) -> dict[str, int]:
        """Вернуть A, B, C, D в порядке полей спецификации."""
        values = dict(zip(FIELD_NAMES, self.operands))
        return {"A": self.operation.opcode, **values}


def validate_operands(operation: Operation, operands: tuple[int, ...]) -> None:
    """Проверить количество аргументов и диапазоны всех полей."""
    if len(operands) != len(operation.widths):
        raise ValueError(f"{operation.name}: неверное число аргументов")
    for index, (value, width) in enumerate(zip(operands, operation.widths)):
        lower, upper = operand_bounds(operation, index, width)
        if not lower <= value <= upper:
            field = FIELD_NAMES[index]
            raise ValueError(f"Поле {field}: нужно {lower}..{upper}")


def operand_bounds(operation: Operation, index: int, width: int) -> tuple:
    """Вернуть диапазон поля; константа LOAD имеет знаковый формат."""
    constant_index = FIELD_NAMES.index("C")
    if operation.name == "LOAD" and index == constant_index:
        return CONSTANT_MIN, CONSTANT_MAX
    return ZERO, (1 << width) - 1

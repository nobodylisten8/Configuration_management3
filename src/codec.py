"""Кодирование и декодирование шестибайтовых инструкций little-endian."""

from src.isa import (
    CONSTANT_BITS,
    INSTRUCTION_BYTES,
    OPCODE_BITS,
    OPERATIONS,
    ZERO,
    Instruction,
    validate_operands,
)

BY_OPCODE = {operation.opcode: operation for operation in OPERATIONS.values()}
CONSTANT_INDEX = 1
SIGN_BIT = 1 << (CONSTANT_BITS - 1)
BYTE_MAX = 255


def encode_instruction(instruction: Instruction) -> bytes:
    """Упаковать поля инструкции, обнуляя все неиспользуемые биты."""
    operation = instruction.operation
    validate_operands(operation, instruction.operands)
    word = operation.opcode
    shift = OPCODE_BITS
    for value, width in zip(instruction.operands, operation.widths):
        word |= (value & ((1 << width) - 1)) << shift
        shift += width
    return word.to_bytes(INSTRUCTION_BYTES, byteorder="little")


def decode_instruction(data: bytes) -> Instruction:
    """Прочитать поля; отклонить неверный размер, opcode и резервные биты."""
    if len(data) != INSTRUCTION_BYTES:
        raise ValueError(f"Нужно {INSTRUCTION_BYTES} байт на инструкцию")
    word = int.from_bytes(data, byteorder="little")
    opcode = word & ((1 << OPCODE_BITS) - 1)
    if opcode not in BY_OPCODE:
        raise ValueError(f"Неизвестный код операции: {opcode}")
    operation = BY_OPCODE[opcode]
    shift = OPCODE_BITS
    operands = []
    for width in operation.widths:
        operands.append((word >> shift) & ((1 << width) - 1))
        shift += width
    if word >> shift != ZERO:
        raise ValueError("Ненулевые резервные биты инструкции")
    if operation.name == "LOAD" and operands[CONSTANT_INDEX] & SIGN_BIT:
        operands[CONSTANT_INDEX] -= 1 << CONSTANT_BITS
    return Instruction(operation, tuple(operands))


def encode_program(instructions: list[Instruction]) -> bytes:
    """Склеить инструкции без заголовка и разделителей."""
    return b"".join(encode_instruction(item) for item in instructions)


def format_bytes(data: bytes) -> str:
    """Форматировать байты аналогично примерам из спецификации."""
    return ", ".join(f"0x{value:02X}" for value in data)

"""Разбор языка: мнемоника и числовые аргументы через запятую."""

from src.isa import OPERATIONS, Instruction, validate_operands


def parse_integer(token: str) -> int:
    """Разобрать десятичное число или число с префиксом 0x/0b/0o."""
    unsigned = token.lstrip("+-").lower()
    base = 0 if unsigned.startswith(("0x", "0b", "0o")) else 10
    try:
        return int(token, base)
    except ValueError as error:
        raise ValueError(f"Некорректное целое число: {token!r}") from error


def parse_line(line: str) -> Instruction | None:
    """Разобрать команду, игнорируя пустые строки и комментарий после ;."""
    text = line.partition(";")[0].strip()
    if not text:
        return None
    parts = text.split(maxsplit=1)
    mnemonic = parts[0].upper()
    if mnemonic not in OPERATIONS:
        raise ValueError(f"Неизвестная команда: {mnemonic}")
    arguments = parts[1:] or [""]
    operands = tuple(parse_integer(item.strip())
                     for item in arguments[0].split(","))
    operation = OPERATIONS[mnemonic]
    validate_operands(operation, operands)
    return Instruction(operation, operands)


def parse_program(source: str) -> list[Instruction]:
    """Разобрать программу и добавить номер строки к сообщению об ошибке."""
    instructions = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        try:
            instruction = parse_line(line)
        except ValueError as error:
            raise ValueError(f"Строка {line_number}: {error}") from error
        if instruction is not None:
            instructions.append(instruction)
    return instructions

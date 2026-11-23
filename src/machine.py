"""Регистровая УВМ с общей адресуемой памятью команд и данных."""

from src.codec import BYTE_MAX, decode_instruction
from src.isa import INSTRUCTION_BYTES, REGISTER_COUNT, ZERO, Instruction

MEMORY_SIZE = 65536


class Machine:
    """Общая память целочисленных ячеек, 128 регистров и счётчик команд."""

    def __init__(self, program: bytes, memory_size: int = MEMORY_SIZE):
        """Загрузить байты кода в начало обнулённой общей памяти."""
        if memory_size <= ZERO or len(program) > memory_size:
            raise ValueError("Программа не помещается в память")
        if len(program) % INSTRUCTION_BYTES != ZERO:
            raise ValueError("Длина программы должна быть кратна 6 байтам")
        self.memory = [ZERO] * memory_size
        self.memory[:len(program)] = program
        self.registers = [ZERO] * REGISTER_COUNT
        self.program_size = len(program)
        self.pc = ZERO

    def check_address(self, address: int) -> None:
        """Не допустить выхода за границы, включая отрицательные индексы."""
        if not ZERO <= address < len(self.memory):
            raise ValueError(f"Адрес вне памяти: {address}")

    def read_memory(self, address: int) -> int:
        """Прочитать одну ячейку общей памяти."""
        self.check_address(address)
        return self.memory[address]

    def write_memory(self, address: int, value: int) -> None:
        """Записать одну ячейку, в том числе в область команд."""
        self.check_address(address)
        self.memory[address] = value

    def fetch(self) -> Instruction:
        """Декодировать следующую команду непосредственно из общей памяти."""
        cells = self.memory[self.pc:self.pc + INSTRUCTION_BYTES]
        if any(not ZERO <= value <= BYTE_MAX for value in cells):
            raise ValueError("Область команды содержит значение вне байта")
        return decode_instruction(bytes(cells))

    def execute(self, instruction: Instruction) -> None:
        """Выбрать обработчик инструкции без цепочки условных операторов."""
        handlers = {
            "LOAD": self.load_constant,
            "READ": self.read_register,
            "STORE": self.store_register,
            "ABS": self.absolute,
        }
        name = instruction.operation.name
        if name not in handlers:
            raise ValueError(f"Операция ещё не реализована: {name}")
        handlers[name](*instruction.operands)

    def run(self) -> None:
        """Выполнять команды по 6 байт до конца исходной области кода."""
        while self.pc < self.program_size:
            try:
                self.execute(self.fetch())
            except ValueError as error:
                raise ValueError(f"PC={self.pc}: {error}") from error
            self.pc += INSTRUCTION_BYTES

    def load_constant(self, destination: int, value: int) -> None:
        """LOAD B, C: записать константу C в регистр B."""
        self.registers[destination] = value

    def read_register(self, pointer: int, destination: int) -> None:
        """READ B, C: прочитать M[R[B]] в R[C]."""
        self.registers[destination] = self.read_memory(self.registers[pointer])

    def store_register(self, source: int, offset: int, pointer: int) -> None:
        """STORE B, C, D: записать R[B] в M[R[D] + C]."""
        self.write_memory(self.registers[pointer] + offset,
                          self.registers[source])

    def absolute(self, source: int, pointer: int) -> None:
        """ABS B, C: записать abs(R[B]) в M[R[C]], сохранив регистры."""
        self.write_memory(self.registers[pointer], abs(self.registers[source]))

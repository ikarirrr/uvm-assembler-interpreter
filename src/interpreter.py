import argparse
import json
from pathlib import Path

# Вариант 32
COMMAND_SIZE = 5
OPCODES = {
    31: "LOAD_CONST",
    55: "READ_MEM",
    40: "WRITE_MEM",
    18: "BITWISE_NOT",
}

def decode_instruction(data):
    """Преобразует 5 байт в команду и операнд."""
    if len(data) != COMMAND_SIZE:
        raise ValueError("Команда должна занимать 5 байт")

    number = int.from_bytes(data, byteorder="little")

    opcode = number & 0b111111
    operand = number >> 6

    if opcode not in OPCODES:
        raise ValueError(f"Неизвестный код операции: {opcode}")

    return opcode, operand

class Interpreter:
    def __init__(self, memory_size=65536):
        # Общая память для команд и данных
        self.memory = [0] * memory_size

        # Регистр-аккумулятор
        self.accumulator = 0

    def load_program(self, binary_data):
        """Загружает машинный код в память."""
        if len(binary_data) % COMMAND_SIZE != 0:
            raise ValueError("Некорректный размер программы")

        if len(binary_data) > len(self.memory):
            raise ValueError("Программа не помещается в память")

        for index, byte in enumerate(binary_data):
            self.memory[index] = byte

        return len(binary_data) // COMMAND_SIZE

    def execute(self, binary_data):
        """Выполняет команды программы по порядку."""
        command_count = self.load_program(binary_data)

        for index in range(command_count):
            position = index * COMMAND_SIZE

            instruction = bytes(
                self.memory[position:position + COMMAND_SIZE]
            )

            opcode, operand = decode_instruction(instruction)

            if opcode == 31:
                # Загрузка константы в аккумулятор
                self.accumulator = operand

            elif opcode == 55:
                # Чтение из памяти по адресу:
                # аккумулятор + смещение
                address = self.accumulator + operand
                self.check_address(address)
                self.accumulator = self.memory[address]

            elif opcode == 40:
                # Запись аккумулятора в память
                self.check_address(operand)
                self.memory[operand] = self.accumulator

            elif opcode == 18:
                # Побитовое НЕ над значением в памяти
                address = self.accumulator
                self.check_address(address)

                self.memory[operand] = (
                    ~self.memory[address]
                ) & 0xFFFFFFFF

        return self.memory

    def check_address(self, address):
        """Проверяет допустимость адреса."""
        if not 0 <= address < len(self.memory):
            raise ValueError(
                f"Адрес {address} выходит за пределы памяти"
            )

    def save_dump(self, path, start, end):
        """Сохраняет дамп выбранной области памяти в JSON."""
        if not 0 <= start <= end <= len(self.memory):
            raise ValueError("Некорректный диапазон памяти")

        dump = {
            str(address): self.memory[address]
            for address in range(start, end)
        }

        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            json.dumps(dump, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )

def main():
    parser = argparse.ArgumentParser(
        description="UVM Interpreter, Variant 32"
    )

    parser.add_argument("binary", help="Binary program path")
    parser.add_argument("dump", help="Memory dump JSON path")
    parser.add_argument(
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        default=[0, 100],
        help="Memory dump range"
    )

    args = parser.parse_args()

    try:
        binary_data = Path(args.binary).read_bytes()

        vm = Interpreter()
        vm.execute(binary_data)

        start, end = args.range
        vm.save_dump(args.dump, start, end)

        print("Program executed successfully.")
        print(f"Accumulator: {vm.accumulator}")
        print(f"Memory dump saved: {args.dump}")

    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

if __name__ == "__main__":
    main()
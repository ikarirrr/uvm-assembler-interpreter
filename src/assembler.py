import argparse
import json
from pathlib import Path

# Команды виртуальной машины, вариант 32
COMMANDS = {
    "LOAD_CONST": {"opcode": 31, "bits": 34},
    "READ_MEM": {"opcode": 55, "bits": 15},
    "WRITE_MEM": {"opcode": 40, "bits": 14},
    "BITWISE_NOT": {"opcode": 18, "bits": 14},
}

def translate(source):
    """
    Перевод текста программы в промежуточное представление.
    """
    instructions = []

    for line_number, line in enumerate(source.splitlines(), 1):
        line = line.split("#", 1)[0].strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 2:
            raise ValueError(
                f"Строка {line_number}: ожидается команда и число"
            )

        command, value_text = parts
        command = command.upper()

        if command not in COMMANDS:
            raise ValueError(
                f"Строка {line_number}: неизвестная команда {command}"
            )

        try:
            value = int(value_text, 0)
        except ValueError:
            raise ValueError(
                f"Строка {line_number}: неверное число {value_text}"
            )

        bits = COMMANDS[command]["bits"]

        if not 0 <= value < 2 ** bits:
            raise ValueError(
                f"Строка {line_number}: число не помещается "
                f"в поле размером {bits} бит"
            )

        instructions.append({
            "command": command,
            "A": COMMANDS[command]["opcode"],
            "B": value
        })

    return instructions

def encode_instruction(instruction):
    """
    Кодирование одной команды в 5 байт.

    Биты 0-5: код операции A.
    Биты 6-39: значение B.
    """
    opcode = instruction["A"]
    value = instruction["B"]

    # Объединяем поля A и B
    machine_code = opcode | (value << 6)

    # Преобразуем число в 5 байт
    return machine_code.to_bytes(5, byteorder="little")

def assemble(instructions):
    """
    Перевод всех команд в машинный код.
    """
    result = bytearray()

    for instruction in instructions:
        result.extend(encode_instruction(instruction))

    return bytes(result)

def main():
    parser = argparse.ArgumentParser(
        description="UVM Assembler, Variant 32"
    )

    parser.add_argument(
        "source",
        help="Path to assembly source file"
    )

    parser.add_argument(
        "output",
        nargs="?",
        help="Path to binary output file"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Print intermediate representation and bytes"
    )

    args = parser.parse_args()

    try:
        source_path = Path(args.source)
        source = source_path.read_text(encoding="utf-8")

        # Этап 1: промежуточное представление
        instructions = translate(source)

        # Этап 2: машинный код
        machine_code = assemble(instructions)

        if args.output:
            output_path = Path(args.output)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            output_path.write_bytes(machine_code)

            print(f"Binary file saved: {output_path}")

        print(f"Binary size: {len(machine_code)} bytes")

        if args.test:
            print("\nIntermediate representation:")
            print(json.dumps(
                instructions,
                ensure_ascii=False,
                indent=4
            ))

            print("\nMachine code:")
            print(" ".join(
                f"0x{byte:02X}" for byte in machine_code
            ))

    except (ValueError, OSError, OverflowError) as error:
        parser.exit(1, f"Error: {error}\n")

if __name__ == "__main__":
    main()
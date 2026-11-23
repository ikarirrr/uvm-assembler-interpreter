import argparse
import json
from pathlib import Path

# Команды виртуальной машины, вариант 32
COMMANDS = {
    "LOAD_CONST": {"opcode": 31, "bits": 36},
    "READ_MEM": {"opcode": 55, "bits": 15},
    "WRITE_MEM": {"opcode": 40, "bits": 14},
    "BITWISE_NOT": {"opcode": 18, "bits": 14},
}

def translate(source):
    """
    Перевод текста программы в промежуточное
    представление.
    """
    instructions = []

    for line_number, line in enumerate(source.splitlines(), 1):
        # Убираем комментарии и пробелы
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

def main():
    parser = argparse.ArgumentParser(
        description="UVM Assembler, Variant 32"
    )

    parser.add_argument(
        "source",
        help="Path to assembly source file"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Print intermediate representation"
    )

    args = parser.parse_args()

    source_path = Path(args.source)
    source = source_path.read_text(encoding="utf-8")

    instructions = translate(source)

    if args.test:
        print(json.dumps(
            instructions,
            ensure_ascii=False,
            indent=4
        ))
    else:
        print("Translation completed successfully.")

if __name__ == "__main__":
    main()
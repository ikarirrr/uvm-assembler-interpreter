import unittest

from src.assembler import (
    COMMANDS,
    translate,
    encode_instruction,
    assemble,
)

class TestAssembler(unittest.TestCase):

    # Проверяем перевод всех команд в JSON-представление
    def test_translate_commands(self):
        source = """
        LOAD_CONST 956
        READ_MEM 330
        WRITE_MEM 36
        BITWISE_NOT 76
        """

        result = translate(source)

        self.assertEqual(len(result), 4)

        for instruction, (name, value) in zip(
            result,
            [
                ("LOAD_CONST", 956),
                ("READ_MEM", 330),
                ("WRITE_MEM", 36),
                ("BITWISE_NOT", 76),
            ],
        ):
            self.assertEqual(instruction["command"], name)
            self.assertEqual(instruction["A"], COMMANDS[name]["opcode"])
            self.assertEqual(instruction["B"], value)

    # Проверяем правильность машинного кода
    def test_machine_code(self):
        examples = [
            ("LOAD_CONST 956", "1fef000000"),
            ("READ_MEM 330", "b752000000"),
            ("WRITE_MEM 36", "2809000000"),
            ("BITWISE_NOT 76", "1213000000"),
        ]

        for source, expected in examples:
            with self.subTest(source=source):
                instruction = translate(source)[0]
                actual = encode_instruction(instruction)
                self.assertEqual(actual.hex(), expected)

    # Каждая команда должна занимать 5 байт
    def test_instruction_size(self):
        instructions = translate(
            "LOAD_CONST 10\nWRITE_MEM 100"
        )

        result = assemble(instructions)

        self.assertEqual(len(result), 10)

    # Проверяем обработку комментариев
    def test_comments(self):
        source = """
        # This is a comment
        LOAD_CONST 10 # Load number

        WRITE_MEM 100
        """

        result = translate(source)

        self.assertEqual(len(result), 2)

    # Проверяем неизвестную команду
    def test_unknown_command(self):
        with self.assertRaises(ValueError):
            translate("UNKNOWN 10")

    # Проверяем неправильное число
    def test_invalid_number(self):
        with self.assertRaises(ValueError):
            translate("LOAD_CONST abc")

    # Проверяем переполнение поля B
    def test_value_overflow(self):
        with self.assertRaises(ValueError):
            translate("WRITE_MEM 16384")

    # Проверяем отрицательные значения
    def test_negative_value(self):
        with self.assertRaises(ValueError):
            translate("LOAD_CONST -1")

if __name__ == "__main__":
    unittest.main()
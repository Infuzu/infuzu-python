import unittest


def add_numbers(a: int, b: int) -> int:
    return a + b


class TestAddNumbers(unittest.TestCase):
    def test_add_positive_numbers(self) -> None:
        self.assertEqual(add_numbers(2, 3), 5)

    def test_add_negative_numbers(self) -> None:
        self.assertEqual(add_numbers(-2, -3), -5)

    def test_add_mixed_numbers(self) -> None:
        self.assertEqual(add_numbers(2, -3), -1)

    def test_add_zero(self) -> None:
        self.assertEqual(add_numbers(0, 0), 0)


if __name__ == "__main__":
    unittest.main()

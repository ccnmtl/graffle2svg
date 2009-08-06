from tests import get_tests
import unittest

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(get_tests())

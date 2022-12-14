import unittest
from my_solution_02 import my_solution

class TestStringMethods(unittest.TestCase):

    def test_my(self):
        self.assertEqual(my_solution(1), 1)
        self.assertEqual(my_solution(2), 3)
        self.assertEqual(my_solution(3), 6)

if __name__ in ['__main__', '__wypp__']:
    unittest.main()

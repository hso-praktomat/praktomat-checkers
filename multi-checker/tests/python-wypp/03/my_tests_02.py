import unittest
from my_solution_02 import my_solution

class TestIt(unittest.TestCase):

    def test_my1(self):
        self.assertEqual(my_solution(1), 1)

    def test_my2(self):
        self.assertEqual(my_solution(2), 3)

    def test_my3(self):
        self.assertEqual(my_solution(3), 6)

if __name__ in ['__main__', '__wypp__']:
    unittest.main()

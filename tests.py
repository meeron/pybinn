import unittest

from pybinn import pybinn

class PyBinnEncodeTests(unittest.TestCase):

    def test_str(self):
        test_str = "test"
        self.assertEqual(test_str, pybinn.loads(pybinn.dumps(test_str)))
        
    def test_str_long(self):
        test_str_long = ",".join(["test"] * 100)
        self.assertEqual(test_str_long, pybinn.loads(pybinn.dumps(test_str_long)))

if __name__ == '__main__':
    unittest.main()
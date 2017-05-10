import unittest
import sys

from pybinn import pybinn

class PyBinnEncodeTests(unittest.TestCase):

    def test_str(self):
        test_str = "test"
        test_str_long = ",".join(["test"] * 100)
        
        self.assertEqual(test_str, pybinn.loads(pybinn.dumps(test_str)))
        self.assertEqual(test_str_long, pybinn.loads(pybinn.dumps(test_str_long)))

    def test_int(self):
        test_uchar = 0x100 - 1
        test_schar = -0x80
        test_ushort = 0x10000 - 1
        test_short = -0x8000
        test_uint = 0x100000000 - 1
        test_int = -0x80000000
        test_ulong = 0x10000000000000000 - 1
        test_long = -0x8000000000000000

        self.assertEqual(test_uchar, pybinn.loads(pybinn.dumps(test_uchar)))
        self.assertEqual(test_schar, pybinn.loads(pybinn.dumps(test_schar)))
        self.assertEqual(test_ushort, pybinn.loads(pybinn.dumps(test_ushort)))
        self.assertEqual(test_short, pybinn.loads(pybinn.dumps(test_short)))
        self.assertEqual(test_uint, pybinn.loads(pybinn.dumps(test_uint)))
        self.assertEqual(test_int, pybinn.loads(pybinn.dumps(test_int)))
        self.assertEqual(test_ulong, pybinn.loads(pybinn.dumps(test_ulong)))
        self.assertEqual(test_long, pybinn.loads(pybinn.dumps(test_long)))

    def test_bool(self):
        test_true = True
        test_false = False

        self.assertEqual(test_true, pybinn.loads(pybinn.dumps(test_true)))
        self.assertEqual(test_false, pybinn.loads(pybinn.dumps(test_false)))

    def test_None(self):
        test_None = None
        
        self.assertEqual(test_None, pybinn.loads(pybinn.dumps(test_None)))

if __name__ == '__main__':
    unittest.main()
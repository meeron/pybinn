import unittest

from pybinn import pybinn

class PyBinnEncodeTests(unittest.TestCase):

    def test_encode_simple_dict(self):
        data = {"hello":"world"}
        encoded_data = pybinn.dumps(data)        
        self.assertEqual(b'\xe2\x11\x01\x05hello\xa0\x05world\x00', encoded_data)

if __name__ == '__main__':
    unittest.main()
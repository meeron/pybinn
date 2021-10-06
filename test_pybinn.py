from time import time
from datetime import datetime
from io import BytesIO

import pybinn


class TestPyBinn:
    """PyBinn tests"""
    
    def setup_method(self, method):
        """Setup method"""
        self._test = [
            True, False, None,
            time(), datetime.utcnow(),
            0, 1, -1, 2, -2, 4, -4, 6, -6,
            0x10, -0x10, 0x20, -0x20, 0x40, -0x40,
            0x80, -0x80, 0x100, -0x100, 0x200, -0x100,
            0x1000, -0x1000, 0x10000, -0x10000,
            0x20000, -0x20000, 0x40000, -0x40000,
            10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000,
            10000000000, 100000000000, 1000000000000,
            -10, -100, -1000, -10000, -100000, -1000000, -10000000, -100000000,
            -1000000000, -10000000000, -100000000000, -1000000000000,
            1.1, 0.1, -0.02, 15.234,
            "hello", "world", "Hello".encode('utf8'), "World".encode('utf8'),
            [1, 2, 3], [], {'name': "Miron", 'age': 32}, {},
            {'a': 1, 'b': 2, 'c': [1, 2, 3]},
            {1: "test1", 2: "test2", 3: "test3"}
        ]

    def test_encode_decode(self):
        """Test encoding and decoding"""
        assert self._test == pybinn.loads(pybinn.dumps(self._test))
    
    def test_encode_decode_using_stream(self):
        with BytesIO() as fp:
            pybinn.dump(self._test, fp)
            fp.seek(0)
            deserialized_obj = pybinn.load(fp)
            assert self._test == deserialized_obj

    def test_user_type(self):
        mock = MockObj("test")
        decoded_mock = pybinn.loads(pybinn.dumps(mock, MockObjEncoder()), MockObjDecoder())
        assert mock.name == decoded_mock.name

    def test_user_type_using_stream(self):
        mock = MockObj("test")
        with BytesIO() as fp:
            pybinn.dump(mock, fp, MockObjEncoder())
            fp.seek(0)
            decoded_mock = pybinn.load(fp, MockObjDecoder())
            assert mock.name == decoded_mock.name

    def test_dict_with_bytes_key(self):
        test_dict = {
            b'12345678': "this is test value"
        }
        assert test_dict == pybinn.loads(pybinn.dumps(test_dict))


class MockObj:
    DATATYPE = b'\xf0'

    def __init__(self, name):
        self.name = name


class MockObjEncoder(pybinn.CustomEncoder):
    def __init__(self):
        super().__init__(MockObj, MockObj.DATATYPE)

    def getbytes(self, value):
        return value.name.encode('utf8')

class MockObjDecoder(pybinn.CustomDecoder):
    def __init__(self):
        super().__init__(MockObj.DATATYPE)

    def getobject(self, data_bytes):
        return MockObj(data_bytes.decode('utf'))

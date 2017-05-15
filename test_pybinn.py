from time import gmtime, time

import pybinn

TEST_OBJ = [
    True, False, None,
    gmtime(),
    0, 1, -1, 2, -2, 4, -4, 6, -6,
    0x10, -0x10, 0x20, -0x20, 0x40, -0x40,
    0x80, -0x80, 0x100, -0x100, 0x200, -0x100,
    0x1000, -0x1000, 0x10000, -0x10000,
    0x20000, -0x20000, 0x40000, -0x40000,
    10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000,
    10000000000, 100000000000, 1000000000000,
    -10, -100, -1000, -10000, -100000, -1000000, -10000000, -100000000,
    -1000000000, -10000000000, -100000000000, -1000000000000,
    1.1, 0.1, -0.02,
    "hello", "world", "Hello".encode('utf8'), "World".encode('utf8'),
    [1, 2, 3], [], {'name': "Miron", 'age': 32}, {},
    {'a': 1, 'b': 2, 'c': [1, 2, 3]}
]

class TestPyBinn:
    """PyBinn tests"""
    def test_encode_decode(self):
        """Test encoding and decoding"""
        assert TEST_OBJ == pybinn.loads(pybinn.dumps(TEST_OBJ))

    def test_performance(self):
        """Performance test"""
        test_dict = {
            'id': 1,
            'name': "test",
            'list': TEST_OBJ
        }
        test_list = []
        for i in range(10000):
            test_list.append(TEST_OBJ)

        encode_time = time()
        data = pybinn.dumps(test_list)
        encode_time = round((time() - encode_time) * 1000)

        decode_time = time()
        pybinn.loads(data)
        decode_time = round((time() - decode_time) * 1000)

        print("Encode: {}ms, Decode: {}ms".format(encode_time, decode_time))
        
        assert True

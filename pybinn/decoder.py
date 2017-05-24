"""Implementation of BINNDecoder"""

import io
from struct import unpack
from time import strptime

import pybinn.datatypes as types

class BINNDecoder(object):
    """BINN <https://github.com/liteserver/binn> decoder for Python"""
    def __init__(self, buffer=None, fp=None):
        if buffer:
            self._buffer = io.BytesIO(buffer)
        if fp:
            self._buffer = fp

    def decode(self):
        """Decode date from buffer"""
        binntype = self._buffer.read(1)
        if binntype == types.BINN_STRING:
            return self._decode_str()
        if binntype == types.BINN_UINT8:
            return unpack('B', self._buffer.read(1))[0]
        if binntype == types.BINN_INT8:
            return unpack('b', self._buffer.read(1))[0]
        if binntype == types.BINN_UINT16:
            return unpack('H', self._buffer.read(2))[0]
        if binntype == types.BINN_INT16:
            return unpack('h', self._buffer.read(2))[0]
        if binntype == types.BINN_UINT32:
            return unpack('I', self._buffer.read(4))[0]
        if binntype == types.BINN_INT32:
            return unpack('i', self._buffer.read(4))[0]
        if binntype == types.BINN_UINT64:
            return unpack('L', self._buffer.read(8))[0]
        if binntype == types.BINN_INT64:
            return unpack('l', self._buffer.read(8))[0]
        if binntype == types.BINN_FLOAT64:
            return unpack('d', self._buffer.read(8))[0]
        if binntype == types.BINN_BLOB:
            return self._decode_bytes()
        if binntype == types.BINN_DATETIME:
            return self._decode_time()
        if binntype == types.BINN_LIST:
            return self._decode_list()
        if binntype == types.BINN_OBJECT:
            return self._decode_dict()
        if binntype == types.BINN_TRUE:
            return True
        if binntype == types.BINN_FALSE:
            return False
        if binntype == types.BINN_NULL:
            return None
        raise TypeError("Invalid Binn data format: {}".format(type))

    def _decode_str(self):
        size = self._from_varint()
        value = self._buffer.read(size).decode('utf8')
        # Ready null terminator byte to advance position
        self._buffer.read(1)
        return value

    def _decode_bytes(self):
        size = unpack('I', self._buffer.read(4))[0]
        return self._buffer.read(size)

    def _decode_time(self):
        time_str = self._decode_str()
        # decode time in UTC timezone
        time_str += "+GMT"
        return strptime(time_str, types.DATETIME_FORMAT + "+%Z")

    def _decode_list(self):
        # read container size
        self._from_varint()
        count = self._from_varint()
        result = []
        for i in range(count):
            result.append(self.decode())
        return result

    def _decode_dict(self):
        # read container size
        self._from_varint()
        count = self._from_varint()
        result = {}
        for i in range(count):
            key_size = unpack('B', self._buffer.read(1))[0]
            key = self._buffer.read(key_size).decode('utf8')
            result[key] = self.decode()
        return result

    def _from_varint(self):
        value = unpack('B', self._buffer.read(1))[0]
        if value & 0x80:
            self._buffer.seek(self._buffer.tell() - 1)
            value = unpack('>I', self._buffer.read(4))[0]
            value &= 0x7FFFFFFF
        return value

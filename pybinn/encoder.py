"""Implementation of BINNEncoder"""

from io import BytesIO
from struct import pack
from time import struct_time, strftime

import pybinn.datatypes as types

class BINNEncoder(object):
    """BINN <https://github.com/liteserver/binn> encoder for Python"""
    def __init__(self):
        self._buffer = BytesIO()

    def encode(self, value):
        """Encode value"""
        self._encode(value)
        return self._buffer.getvalue()

    def _encode(self, value):
        value_type = type(value)
        if value_type == type(None):
            self._buffer.write(types.BINN_NULL)
            return
        if value_type is str:
            self._encode_str(value)
            return
        if value_type is int:
            self._encode_int(value)
            return
        if value_type is bool:
            self._encode_bool(value)
            return
        if value_type is float:
            self._encode_float(value)
            return
        if value_type is bytes:
            self._encode_bytes(value)
            return
        if value_type is struct_time:
            self._encode_time(value)
            return
        if value_type is list:
            self._encode_list(value)
            return
        if value_type is dict:
            self._encode_dict(value)
            return
        raise TypeError("Invalid type for encode: {}".format(value_type))

    def _encode_str(self, value, data_type=types.BINN_STRING):
        size = len(value.encode('utf8'))
        self._buffer.write(data_type)
        self._buffer.write(self._to_varint(size))
        self._buffer.write(value.encode('utf8') + b'\0')

    def _encode_uint(self, value):
        # unsigned char (byte)
        if value < 0x100:
            self._buffer.write(types.BINN_UINT8)
            self._buffer.write(pack('B', value))
            return
        # unsigned short
        if value < 0x10000:
            self._buffer.write(types.BINN_UINT16)
            self._buffer.write(pack('H', value))
            return
        # unsigned int
        if value < 0x100000000:
            self._buffer.write(types.BINN_UINT32)
            self._buffer.write(pack('I', value))
            return
        # unsigned long
        if value < 0x10000000000000000:
            self._buffer.write(types.BINN_UINT64)
            self._buffer.write(pack('L', value))
            return
        raise OverflowError("Value to big {}.".format(hex(value)))

    def _encode_int(self, value):
        if value >= 0:
            return self._encode_uint(value)
        # signed char
        if value >= -0x80:
            self._buffer.write(types.BINN_INT8)
            self._buffer.write(pack('b', value))
            return
        # short
        if value >= -0x8000:
            self._buffer.write(types.BINN_INT16)
            self._buffer.write(pack('h', value))
            return
        # int
        if value >= -0x80000000:
            self._buffer.write(types.BINN_INT32)
            self._buffer.write(pack('i', value))
            return
        # long
        if value >= -0x8000000000000000:
            self._buffer.write(types.BINN_INT64)
            self._buffer.write(pack('l', value))

    def _encode_bool(self, value):
        if value:
            self._buffer.write(types.BINN_TRUE)
        if not value:
            self._buffer.write(types.BINN_FALSE)

    def _encode_float(self, value):
        self._buffer.write(types.BINN_FLOAT64)
        self._buffer.write(pack('d', value))

    def _encode_bytes(self, value):
        self._buffer.write(types.BINN_BLOB)
        self._buffer.write(pack('I', len(value)))
        self._buffer.write(value)

    def _encode_time(self, value):
        time_str = strftime(types.DATETIME_FORMAT, value)
        self._encode_str(time_str, types.BINN_DATETIME)

    def _encode_list(self, value):
        # TOOD: write proper size
        self._buffer.write(types.BINN_LIST)
        self._buffer.write(self._to_varint(0))
        self._buffer.write(self._to_varint(len(value)))

        for item in value:
            self._encode(item)

    def _encode_dict(self, value):
        self._buffer.write(types.BINN_OBJECT)
        # TOOD: write proper size
        self._buffer.write(self._to_varint(0))
        self._buffer.write(self._to_varint(len(value)))

        for key in value:
            if len(key) > 255:
                raise OverflowError("Key '{}' is to big. Max length is 255.".format(key))
            self._buffer.write(pack('B', len(key)))
            self._buffer.write(key.encode('utf8'))
            self._encode(value[key])

    def _to_varint(self, value):
        if value > 127:
            return pack('>I', value | 0x80000000)
        return pack('B', value)

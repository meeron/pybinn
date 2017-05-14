import io, time
from struct import pack, unpack

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Data Formats
BINN_OBJECT     = b'\xe2'
BINN_LIST       = b'\xe0'

BINN_STRING     = b'\xa0'
BINN_DATETIME   = b'\xa1' # in DATETIME_FORMAT format

BINN_BLOB       = b'\xc0'

BINN_NULL       = b'\x00'
BINN_TRUE       = b'\x01'
BINN_FALSE      = b'\x02'

BINN_UINT8      = b'\x20'
BINN_INT8       = b'\x21'
BINN_UINT16     = b'\x40'
BINN_INT16      = b'\x41'
BINN_UINT32     = b'\x60'
BINN_INT32      = b'\x61'
BINN_UINT64     = b'\x80'
BINN_INT64      = b'\x81'
BINN_FLOAT64    = b'\x82'

class _Encoder(object):
    def __init__(self):
        self._buffer = io.BytesIO()

    def encode(self, value):
        self._encode(value)
        return self._buffer.getvalue()

    def _encode(self, value):
        value_type = type(value)
        if value_type == type(None):
            self._buffer.write(BINN_NULL)
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
        if value_type is time.struct_time:
            self._encode_time(value)
            return
        if value_type is list:
            self._encode_list(value)
            return
        if value_type is dict:
            self._encode_dict(value)
            return
        raise TypeError("Invalid type for encode: {}".format(value_type))

    def _encode_str(self, value, data_type=BINN_STRING):
        size = len(value.encode('utf8'))
        self._buffer.write(data_type)
        self._buffer.write(self._to_varint(size))
        self._buffer.write(value.encode('utf8') + b'\0')

    def _encode_uint(self, value):
        # unsigned char (byte)
        if value < 0x100:
            self._buffer.write(BINN_UINT8)
            self._buffer.write(pack('B', value))
            return
        # unsigned short
        if value < 0x10000:
            self._buffer.write(BINN_UINT16)
            self._buffer.write(pack('H', value))
            return
        # unsigned int
        if value < 0x100000000:
            self._buffer.write(BINN_UINT32)
            self._buffer.write(pack('I', value))
            return
        # unsigned long
        if value < 0x10000000000000000:
            self._buffer.write(BINN_UINT64)
            self._buffer.write(pack('L', value))
            return
        raise OverflowError("Value to big {}.".format(hex(value)))

    def _encode_int(self, value):
        if value >= 0:
            return self._encode_uint(value)
        # signed char
        if value >= -0x80:
            self._buffer.write(BINN_INT8)
            self._buffer.write(pack('b', value))
            return
        # short
        if value >= -0x8000:
            self._buffer.write(BINN_INT16)
            self._buffer.write(pack('h', value))
            return
        # int
        if value >= -0x80000000:
            self._buffer.write(BINN_INT32)
            self._buffer.write(pack('i', value))
            return
        # long
        if value >= -0x8000000000000000:
            self._buffer.write(BINN_INT64)
            self._buffer.write(pack('l', value))

    def _encode_bool(self, value):
        if value:
            self._buffer.write(BINN_TRUE)
        if not value:
            self._buffer.write(BINN_FALSE)

    def _encode_float(self, value):
        self._buffer.write(BINN_FLOAT64)
        self._buffer.write(pack('d', value))

    def _encode_bytes(self, value):
        self._buffer.write(BINN_BLOB)
        self._buffer.write(pack('I', len(value)))
        self._buffer.write(value)

    def _encode_time(self, value):
        time_str = time.strftime(DATETIME_FORMAT, value)
        self._encode_str(time_str, BINN_DATETIME)

    def _encode_list(self, value):
        with io.BytesIO() as buffer:        
            for item in value:
                buffer.write(_Encoder().encode(item))

            self._buffer.write(BINN_LIST)        
            self._buffer.write(self._to_varint(buffer.tell() + 3))
            self._buffer.write(self._to_varint(len(value)))
            self._buffer.write(buffer.getvalue())

    def _encode_dict(self, value):
        with io.BytesIO() as buffer:
            for key in value:
                if len(key) > 255:
                    raise OverflowError("Key '{}' is to big. Max length is 255.".format(key))
                buffer.write(pack('B', len(key)))
                buffer.write(key.encode('utf8'))        
                buffer.write(_Encoder().encode(value[key]))

            self._buffer.write(BINN_OBJECT)        
            self._buffer.write(self._to_varint(buffer.tell() + 3))
            self._buffer.write(self._to_varint(len(value)))
            self._buffer.write(buffer.getvalue())


    def _to_varint(self, value):
        if value > 127:
            return pack('>I', value | 0x80000000)
        return pack('B', value)

class _Decoder(object):
    def __init__(self, buffer):
        self._buffer = io.BytesIO(buffer)

    def decode(self):
        type = self._buffer.read(1)
        if type == BINN_STRING:
            return self._decode_str()
        if type == BINN_UINT8:
            return unpack('B', self._buffer.read(1))[0]
        if type == BINN_INT8:
            return unpack('b', self._buffer.read(1))[0]
        if type == BINN_UINT16:
            return unpack('H', self._buffer.read(2))[0]
        if type == BINN_INT16:
            return unpack('h', self._buffer.read(2))[0]
        if type == BINN_UINT32:
            return unpack('I', self._buffer.read(4))[0]
        if type == BINN_INT32:
            return unpack('i', self._buffer.read(4))[0]
        if type == BINN_UINT64:
            return unpack('L', self._buffer.read(8))[0]
        if type == BINN_INT64:
            return unpack('l', self._buffer.read(8))[0]
        if type == BINN_FLOAT64:
            return unpack('d', self._buffer.read(8))[0]
        if type == BINN_BLOB:
            return self._decode_bytes()
        if type == BINN_DATETIME:
            return self._decode_time()
        if type == BINN_LIST:
            return self._decode_list()
        if type == BINN_OBJECT:
            return self._decode_dict()
        if type == BINN_TRUE:
            return True
        if type == BINN_FALSE:
            return False
        if type == BINN_NULL:
            return None
        raise TypeError("Invalid Binn data format: {}".format(type))

    def _decode_str(self):
        size = self._from_varint()
        value = str(self._buffer.read(size), 'utf8')
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
        return time.strptime(time_str, DATETIME_FORMAT + "+%Z")

    def _decode_list(self):
        size = self._from_varint()
        count = self._from_varint()
        result = []
        for i in range(count):
            result.append(self.decode())
        return result

    def _decode_dict(self):         
        size = self._from_varint()
        count = self._from_varint()
        result = {}
        for i in range(count):
            key_size = unpack('B', self._buffer.read(1))[0] 
            key = str(self._buffer.read(key_size), 'utf8')
            result[key] = self.decode()
        return result        

    def _from_varint(self):
        value = unpack('B', self._buffer.read(1))[0]
        if value & 0x80:
            self._buffer.seek(self._buffer.tell() - 1)
            value = unpack('>I', self._buffer.read(4))[0]
            value &= 0x7FFFFFFF
        return value
    
def dumps(value):
    return _Encoder().encode(value)

def loads(buffer):
    return _Decoder(buffer).decode()
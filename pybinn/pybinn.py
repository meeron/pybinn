import io

# Data Formats
BINN_OBJECT = b'\xe2'

BINN_STRING = b'\xa0'

class _Encoder(object):
    def __init__(self):
        self._buffer = io.BytesIO()

    def encode(self, value):
        self._encode(value)
        return self._buffer.getvalue()

    def _encode(self, value):
        value_type = type(value)
        if value_type is str:
            self._encode_str(value)

    def _encode_str(self, value):
        size = len(value.encode('utf8'))
        self._buffer.write(BINN_STRING)
        self._buffer.write(self._to_varint(size))
        self._buffer.write(value.encode('utf8') + b'\0')

    def _to_varint(self, value):
        if value > 127:
            return (value | 0x80000000).to_bytes(4,'big')
        return value.to_bytes(1, 'big')

class _Decoder(object):
    def __init__(self, buffer):
        self._buffer = io.BytesIO(buffer)

    def decode(self):
        type = self._buffer.read(1)
        if type == BINN_STRING:
            return self._decode_str()
        return None

    def _decode_str(self):
        size = self._from_varint()
        value = str(self._buffer.read(size), 'utf8')
        # Ready null terminator byte to advance position
        self._buffer.read(1)
        return value

    def _from_varint(self):
        value = int.from_bytes(self._buffer.read(1), 'big')
        if value & 0x80:
            self._buffer.seek(self._buffer.tell() - 1)
            value = int.from_bytes(self._buffer.read(4), 'big')
            value &= 0x7FFFFFFF
        return value
    
def dumps(value):
    return _Encoder().encode(value)

def loads(buffer):
    return _Decoder(buffer).decode()
import io

# Data Formats
BINN_OBJECT = b'\xe2'

BINN_STRING = b'\xa0'

def _int_to_bytes(value):
    return value.to_bytes(1, 'big')

def dumps(value, bytes_io=None):
    value_type = type(value)
    size = 0
    count = 0

    # String
    if value_type is str:
        size = len(value.encode('utf8'))
        # Store the type
        bytes_io.write(BINN_STRING)
        # Store the size
        bytes_io.write(_int_to_bytes(size))
        # Store the string
        bytes_io.write(value.encode('utf8') + b'\0')        
        return None

    # Dictionary
    if value_type is dict:

        dict_bytes_io = io.BytesIO()
        bytes_io = io.BytesIO()

        # Store the dict type
        bytes_io.write(BINN_OBJECT)

        count = len(value)

        for key in value:
            # Store the key
            size = len(key.encode('utf8'))
            if size > 255:
                raise OverflowError("Key '{}' is to long".format(key))
            dict_bytes_io.write(_int_to_bytes(size))
            dict_bytes_io.write(key.encode('utf8'))
            dumps(value[key], dict_bytes_io)
        
        size = dict_bytes_io.tell()

        # Store container size
        bytes_io.write(_int_to_bytes(size))
        # Store key/value pairs
        bytes_io.write(_int_to_bytes(count))
        # Store content
        bytes_io.write(dict_bytes_io.getvalue())

        return bytes_io.getvalue()

    raise NotImplementedError("Not supported type: {}".format(value_type))

def loads(buffer):
    return None
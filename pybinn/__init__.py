"""BINN (https://github.com/liteserver/binn) serialization/deserialization module"""

__version__ = '0.9.1'
__all__ = [
    'dumps', 'loads', 'dump', 'load',
    'BINNDecoder', 'BINNEncoder',
]

__author__ = 'Miron Jakubowski <mijakubowski@gmail.com>'

from .encoder import BINNEncoder
from .decoder import BINNDecoder

def dumps(value):
    """Serialize ``value`` to BINN format and returns bytes"""
    return BINNEncoder().encode_bytes(value)

def dump(value, fp):
    """Serialize ``value`` to BINN format and saves bytes to stream ``fp``"""
    BINNEncoder(fp).encode(value)

def loads(buffer):
    """Deserialize buffer in BINN format and return object"""
    return BINNDecoder(buffer).decode()

def load(fp):
    """Deserialize stream and return object"""
    return BINNDecoder(None, fp).decode()

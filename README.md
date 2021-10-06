pybinn
======
[![Build Status](https://app.travis-ci.com/meeron/pybinn.svg?branch=master)](https://app.travis-ci.com/meeron/pybinn)

Python wrapper for BINN serialization (https://github.com/liteserver/binn)

Usage
-----

Encoding

```python
import pybinn

data = pybinn.dumps({'hello':"world", 'id':12})
print(data)
# b'\xe2\x16\x02\x02id \x0c\x05hello\xa0\x05world\x00'
```

Decoding

```python
data = b'\xe2\x16\x02\x02id \x0c\x05hello\xa0\x05world\x00 '
obj = pybinn.loads(data)
print(obj)
# {'id': 12, 'hello': 'world'}
```

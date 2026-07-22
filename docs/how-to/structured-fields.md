# How to work with Structured Fields

[RFC 9651 Structured Field Values](https://www.rfc-editor.org/rfc/rfc9651) is the type system
that modern HTTP headers are built on. `http-fields` ships a standalone implementation in
`http_fields.structuredfields`, plus header classes that use it.

## Use the Structured-Fields headers

These behave like any other header:

```python
from http_fields import Priority, CacheStatus, ContentDigest
import base64

Priority.parse("u=5, i").urgency        # 5
Priority(urgency=5, incremental=True).value    # 'u=5, i'

digest = base64.b64encode(b"hello").decode()
cd = ContentDigest.parse(f"sha-256=:{digest}:")
cd.digests                               # (('sha-256', b'hello'),)

cs = CacheStatus.parse("ExampleCache; hit; ttl=376")
cs.members[0].value                      # 'ExampleCache' (a Token)
cs.members[0].parameters                 # (('hit', True), ('ttl', 376))
```

## Parse and serialize raw Structured Fields

Use the `parse_*` / `serialize_*` functions directly for the three top-level types — Item, List,
and Dictionary:

```python
from http_fields.structuredfields import (
    parse_item, parse_list, parse_dictionary,
    serialize_item, serialize_list, serialize_dictionary,
)

parse_item("5;foo=bar")          # Item(value=5, parameters=(('foo', Token('bar')),))
parse_list("a, b, (c d);x=1")    # tuple of Item / InnerList
parse_dictionary("a=1, b, c=?0") # tuple of (key, Item / InnerList) pairs
```

Bare items map to native Python types:

| Structured Fields type | Python type |
|---|---|
| Integer | `int` |
| Decimal | `decimal.Decimal` |
| String | `str` |
| Token | `Token` (a `str` subclass) |
| Boolean | `bool` |
| Byte Sequence | `bytes` |
| Date | `datetime.datetime` |
| Display String | `DisplayString` (a `str` subclass) |

`Token` and `DisplayString` are distinct `str` subclasses so they serialize correctly (a `Token`
is bare, a `str` is quoted):

```python
from http_fields.structuredfields import Item, Token, serialize_item

serialize_item(Item(Token("gzip")))   # 'gzip'
serialize_item(Item("gzip"))          # '"gzip"'
```

## Build values from scratch

Compose `Item` / `InnerList` and serialize:

```python
from http_fields.structuredfields import Item, InnerList, Token, serialize_list

members = (Item(Token("sugar")), InnerList((Item(1), Item(2)), (("x", True),)))
serialize_list(members)               # 'sugar, (1 2);x'
```

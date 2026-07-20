# Getting started

This tutorial walks you through the core of `http-headers`: parsing a header, reading its
structured fields, building one from scratch, and turning it back into bytes. By the end you'll
understand the shape shared by every header in the library.

## Install

```sh
uv add http-headers
# or: pip install http-headers
```

## 1. Parse a header

Every known header has a `.parse()` classmethod that takes the raw header *value* (not the whole
`Name: value` line) and returns a validated instance:

```python
from http_headers import ContentType

ct = ContentType.parse("text/html; charset=UTF-8")
```

The pieces are now structured attributes:

```python
ct.type       # 'text'
ct.subtype    # 'html'
ct.charset    # 'UTF-8'   (compares case-insensitively)
```

Invalid input raises `ValueError`:

```python
ContentType.parse("not-a-media-type")   # ValueError: Invalid ContentType value "..."
```

## 2. Serialize it back

`str(header)` gives the full field line; `bytes(header)` encodes it; `.value` is just the value
part; `.asgi_value` is a `(name, value)` pair of ASCII bytes ready for an ASGI `send` dict:

```python
str(ct)          # 'Content-Type: text/html;charset=UTF-8'
ct.value         # 'text/html;charset=UTF-8'
bytes(ct)        # b'Content-Type: text/html;charset=UTF-8'
ct.asgi_value    # (b'Content-Type', b'text/html;charset=UTF-8')
```

## 3. Build one from pieces

You don't have to start from a string. Simple headers take their field directly; richer ones
provide a builder classmethod (here, `ContentType.of(...)`):

```python
from http_headers import Age, ContentType

Age(60)                                              # a scalar header takes its value
ContentType.of(type="text", subtype="html", charset="utf-8")
```

Both paths validate, so you can't build a malformed header:

```python
Age(-1)   # ValueError: Value must be non-negative.
```

## 4. Dispatch by name

If you have a header name and value (say, from an incoming request) and don't know the type up
front, `Header.create()` returns the right subclass — or a `CustomHeader` for an unrecognized
name:

```python
from http_headers import Header

Header.create("content-type", "text/plain")   # -> ContentType(...)
Header.create("x-request-id", "abc123")        # -> CustomHeader(...)
```

## 5. Headers are values

Every header is a frozen dataclass: immutable, comparable, and hashable.

```python
from http_headers import Age

Age(1) == Age(1)          # True
len({Age(1), Age(1)})     # 1  (deduplicates)
Age(1).seconds = 2        # dataclasses.FrozenInstanceError
```

## Where to go next

- [Parse and build headers](../how-to/parse-and-build-headers.md) — the three construction styles
  in detail.
- [Header catalog](../reference/headers.md) — find the header you need and how to build it.
- [Explanation: the header model](../explanation/design.md) — why it's shaped this way.

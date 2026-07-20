# How to handle custom and unknown headers

## Dispatch an incoming header by name

When you receive a `(name, value)` pair and don't know the type ahead of time, use
`Header.create()`. It matches the name (case-insensitively) against the known headers and returns
that subclass, falling back to `CustomHeader` for anything unrecognized:

```python
from http_headers import Header, ContentType, CustomHeader

h = Header.create("Content-Type", "text/plain")
isinstance(h, ContentType)     # True

h = Header.create("X-Request-Id", "abc123")
isinstance(h, CustomHeader)    # True
```

`create()` validates the value through the matched header's `parse()`, so an invalid known-header
value still raises `ValueError`.

## Represent an arbitrary header

`CustomHeader` models any header with a non-standard field name. Its name and value are validated
as an RFC 9110 `field-name` / `field-value`:

```python
from http_headers import CustomHeader

h = CustomHeader("X-Request-Id", "abc123")
h.name          # 'X-Request-Id'
h.value         # 'abc123'
str(h)          # 'X-Request-Id: abc123'
h.asgi_value    # (b'X-Request-Id', b'abc123')

CustomHeader("bad name", "v")   # ValueError: Invalid field-name "bad name".
```

## Iterate the known headers

`Header.subclass_tree()` yields every registered header class, which is handy for tooling or
introspection:

```python
from http_headers import Header

names = sorted(
    c.name for c in Header.subclass_tree()
    if isinstance(getattr(c, "name", None), str)
)
```

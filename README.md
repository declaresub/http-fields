# http-headers

Typed, validated HTTP headers for Python. Each header is an immutable
[dataclass](https://docs.python.org/3/library/dataclasses.html) whose fields are the
structured components of the header. [abnf](https://pypi.org/project/abnf/) grammars are used
both to **parse** incoming header strings and to **validate** field values, so a constructed
header is always well-formed.

Requires Python 3.10+.

## Install

```sh
uv add http-headers
# or: pip install http-headers
```

## Quick start

```python
from http_headers import Age, ContentType, SetCookie, Header, CustomHeader

# Parse a raw header value string with .parse()
age = Age.parse("60")
age.seconds                      # NonNegativeInt(60)
str(age)                         # 'age: 60'

# Read structured fields
ct = ContentType.parse("text/html; charset=UTF-8")
ct.type, ct.subtype              # ('text', 'html')
ct.charset                       # 'UTF-8'  (case-insensitive comparisons)

# Build from pieces
ContentType.of(type="text", subtype="html", charset="utf-8")
Age(60)                          # a scalar header takes its field directly

# Headers with a rich constructor expose .build()
SetCookie.build(cookie_name="SID", cookie_value="abc", path="/", secure=True).value
# 'SID=abc; Path=/; SameSite=Lax; Secure'
```

### Construction, three ways

| Form | Use it for | Validates |
|---|---|---|
| `Header.parse(value)` | a raw header value string | ✅ (via the abnf grammar) |
| `Header(fields…)` / `Header.of(…)` / `Header.build(…)` | building from structured pieces | ✅ (via the field types) |
| `Header.create(name, value)` | dispatch by header name | ✅ |

`.parse()` is the only string entry point. Direct construction takes the structured fields
(scalars accept plain values and coerce them, e.g. `Age(60)` → `NonNegativeInt`). Headers whose
piece-wise construction is richer than their stored fields provide a builder classmethod
(`ContentType.of(...)`, `SetCookie.build(...)`, `ContentDisposition.build(...)`).

### Dispatch by name

`Header.create(name, value)` returns the matching header subclass, or a `CustomHeader` for an
unrecognized name:

```python
Header.create("content-type", "text/plain")   # -> ContentType(...)
Header.create("x-request-id", "abc123")        # -> CustomHeader(...)
```

`CustomHeader` represents any header with an arbitrary field name; its name and value are
validated as an RFC 9110 `field-name` / `field-value`:

```python
h = CustomHeader("X-Request-Id", "abc123")
str(h)          # 'X-Request-Id: abc123'
bytes(h)        # b'X-Request-Id: abc123'
h.asgi_value    # (b'X-Request-Id', b'abc123')  -- ready for an ASGI send dict
```

### Immutable, hashable, comparable

Headers are frozen: they compare by value, hash, and cannot be mutated in place.

```python
Age(1) == Age(1)          # True
len({Age(1), Age(1)})     # 1
Age(1).seconds = 2        # dataclasses.FrozenInstanceError
```

### Validation

Invalid input raises `ValueError` (or `TypeError` for wrong argument types):

```python
Age(-1)                       # ValueError: Value must be non-negative.
CustomHeader("bad name", "v") # ValueError: Invalid field-name "bad name".
ContentType.parse("nope")     # ValueError: Invalid ContentType value "nope".
```

## Supported headers

`Accept`, `AcceptCharset`, `AcceptEncoding`, `AcceptRanges`, `Age`, `Allow`,
`AuthenticationInfo`, `Authorization`, `CacheControl`, `Connection`, `ContentDisposition`,
`ContentEncoding`, `ContentLength`, `ContentRange`, `ContentType`, `Cookie`, `Date`, `ETag`,
`Expires`, `Host`, `IfMatch`, `IfModifiedSince`, `IfNoneMatch`, `IfUnmodifiedSince`,
`LastModified`, `Location`, `RetryAfter`, `SetCookie`, `UserAgent`, `Vary`, `WWWAuthenticate`,
plus `CustomHeader` for anything else.

## Development

This project uses [uv](https://docs.astral.sh/uv/):

```sh
uv sync                       # create the environment
uv run pytest                 # run the tests
uv run ruff check .           # lint
uv run ruff format .          # format
uv run basedpyright           # type-check
uv run --python 3.13 pytest   # run the suite on another supported version
```

The design of the header model is documented in
[docs/design/header-model.md](docs/design/header-model.md).

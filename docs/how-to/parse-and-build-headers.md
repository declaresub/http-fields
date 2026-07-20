# How to parse and build headers

There are three ways to get a header instance. This guide shows when to use each.

## Parse a raw value string

`Header.parse(value)` is the only string entry point. It validates against the header's abnf
grammar and raises `ValueError` on bad input.

```python
from http_headers import CacheControl

cc = CacheControl.parse("max-age=3600, no-cache, immutable")
cc.max_age       # 3600
cc.no_cache      # True
cc.immutable     # True
```

Pass the header *value* only — not the `Name: value` line.

## Construct from structured fields

Direct construction takes the header's fields. Scalars coerce plain values; list-style headers
take varargs.

```python
from http_headers import Age, Connection, Vary

Age(60)                          # coerced to NonNegativeInt
Connection("keep-alive", "close")
Vary("accept-encoding", "accept-language")
```

Union-typed headers accept either member:

```python
from datetime import datetime, timezone
from http_headers import RetryAfter, Date

RetryAfter(120)                                          # delay-seconds
RetryAfter(datetime(2030, 1, 1, tzinfo=timezone.utc))    # HTTP-date
Date(datetime(2030, 1, 1, tzinfo=timezone.utc))
```

## Use a builder classmethod

Headers whose piece-wise construction is richer than their stored fields expose a builder:

| Header | Builder |
|---|---|
| `ContentType` | `ContentType.of(type, subtype, *, charset=None, boundary=None, params=None)` |
| `SetCookie` | `SetCookie.build(cookie_name, cookie_value, *, domain=None, path=None, expires=None, max_age=None, secure=False, http_only=False, samesite="Lax", extension=None)` |
| `ContentDisposition` | `ContentDisposition.build(disposition_type, disposition_parms=None)` |
| `ETag` | `ETag.from_tag(tag, weak=False)` |

```python
from http_headers import ContentType, SetCookie, ETag

ContentType.of(type="text", subtype="html", charset="utf-8")
SetCookie.build(cookie_name="SID", cookie_value="abc", path="/", secure=True)
ETag.from_tag("deadbeef", weak=True)
```

`.build()` validates its input strictly (raising `TypeError`/`ValueError`); `SetCookie.parse()`
uses the more lenient RFC 6265 §5 algorithm for interoperability.

## Wildcard headers

`If-Match` / `If-None-Match` use `wildcard=True` for `*`; `AltSvc` uses `clear=True` for `clear`:

```python
from http_headers import IfMatch, AltSvc
from http_headers.visitors.rfc9110 import EntityTag

IfMatch(wildcard=True)                 # "*"
IfMatch(EntityTag("deadbeef"))         # a specific tag
AltSvc(clear=True)                     # "clear"
```

## Serialize

Any header round-trips to text and bytes:

```python
str(cc)         # 'Cache-Control: max-age=3600,no-cache,immutable'
cc.value        # 'max-age=3600,no-cache,immutable'
bytes(cc)       # b'Cache-Control: ...'
cc.asgi_value   # (b'Cache-Control', b'...')
```

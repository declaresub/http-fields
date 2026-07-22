# How to parse and build headers

There are three ways to get a header instance. This guide shows when to use each.

## Parse a raw value string

`Header.parse(value)` is the only string entry point. It validates against the header's abnf
grammar and raises `ValueError` on bad input.

```python
from http_fields import CacheControl

cc = CacheControl.parse("max-age=3600, no-cache, immutable")
cc.max_age       # 3600
cc.no_cache      # True
cc.immutable     # True
```

Pass the header *value* only — not the `Name: value` line.

## Construct from parsed fields

`parse()` is the entry point for *strings*. Direct construction takes each field as its
already-parsed type — a leaf type or value object — so a constructor never re-runs the grammar
on untrusted text. Passing a raw string where a typed field is expected raises `TypeError`
pointing you back to `parse()`.

Plain scalars still coerce their natural Python value:

```python
from datetime import datetime, timezone
from http_fields import Age, Date, RetryAfter

Age(60)                                                  # int -> NonNegativeInt
Date(datetime(2030, 1, 1, tzinfo=timezone.utc))          # a datetime
RetryAfter(120)                                          # delay-seconds ...
RetryAfter(datetime(2030, 1, 1, tzinfo=timezone.utc))    # ... or an HTTP-date
```

List-style headers take their leaf types as varargs. Build the leaves (each validates itself),
or `parse()` a whole value string:

```python
from http_fields import Connection, FieldName, Token, Vary

Connection(Token("keep-alive"), Token("close"))
Vary(FieldName("accept-encoding"), FieldName("accept-language"))

Connection.parse("keep-alive, close")                    # from a raw string
```

`Connection("keep-alive")` — a bare string — is now a `TypeError`; use `Connection.parse(...)`.

Headers with structured values take value objects, which coerce their string parts to validated
leaves:

```python
from http_fields import Protocol, Upgrade

Upgrade(Protocol("HTTP", "2"), Protocol("WebSocket"))
Upgrade.parse("HTTP/2, WebSocket")                       # equivalent, from a string
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
from http_fields import ContentType, SetCookie, ETag

ContentType.of(type="text", subtype="html", charset="utf-8")
SetCookie.build(cookie_name="SID", cookie_value="abc", path="/", secure=True)
ETag.from_tag("deadbeef", weak=True)
```

`.build()` validates its input strictly (raising `TypeError`/`ValueError`); `SetCookie.parse()`
uses the more lenient RFC 6265 §5 algorithm for interoperability.

## Wildcard headers

`If-Match` / `If-None-Match` use `wildcard=True` for `*`; `AltSvc` uses `clear=True` for `clear`:

```python
from http_fields import IfMatch, AltSvc
from http_fields.visitors.rfc9110 import EntityTag

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

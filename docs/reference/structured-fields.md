# `http_headers.structuredfields`

An implementation of [RFC 9651 Structured Field Values for HTTP](https://www.rfc-editor.org/rfc/rfc9651):
a value model plus parse and serialize functions for the three top-level types (Item, List,
Dictionary). Used by `Priority`, `CacheStatus`, `ProxyStatus`, `ContentDigest`, and `ReprDigest`,
and usable on its own for any Structured-Fields header.

## Value types

- **`Item`** — `Item(value, parameters=())`. A bare item together with its parameters.
- **`InnerList`** — `InnerList(items=(), parameters=())`. An ordered list of `Item`s with
  parameters, e.g. `(a b);q=1`.
- **`Token`** — a `str` subclass for a Structured Fields Token (unquoted identifier).
- **`DisplayString`** — a `str` subclass for a Display String (Unicode text).

`parameters` is an ordered tuple of `(key, bare-item)` pairs. A member of a List or Dictionary is
either an `Item` or an `InnerList`.

### Bare item ↔ Python type

| Structured Fields type | Python type |
|---|---|
| Integer | `int` |
| Decimal | `decimal.Decimal` |
| String | `str` |
| Token | `Token` (subclass of `str`) |
| Boolean | `bool` |
| Byte Sequence | `bytes` |
| Date | `datetime.datetime` (UTC) |
| Display String | `DisplayString` (subclass of `str`) |

`Token` and `DisplayString` are distinct subclasses so a Token serializes bare while a plain
`str` serializes as a quoted String.

## Parsing

- **`parse_item(value)` → `Item`**
- **`parse_list(value)` → `tuple[Item | InnerList, ...]`** — an empty string is an empty list.
- **`parse_dictionary(value)` → `tuple[tuple[str, Item | InnerList], ...]`** — ordered
  `(key, member)` pairs; an empty string is an empty dictionary.

A bare Dictionary key or bare parameter denotes Boolean `True`.

## Serializing

- **`serialize_item(item)` → `str`**
- **`serialize_list(members)` → `str`** — `members` is a tuple of `Item` / `InnerList`.
- **`serialize_dictionary(members)` → `str`** — `members` is a tuple of `(key, Item / InnerList)`.
- **`serialize_bare(value)` → `str`** — serialize a single bare item.

Parsing then serializing reproduces the canonical form (RFC 9651 §4.1), including String
escaping, Display String percent-encoding, Byte Sequence base64, and Dates.

## Example

```python
from http_headers.structuredfields import parse_dictionary, serialize_dictionary

members = parse_dictionary('a=1, b, c=(1 2);y')
serialize_dictionary(members)   # 'a=1, b, c=(1 2);y'
```

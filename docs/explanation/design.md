# The header model

This page explains *why* `http-fields` is shaped the way it is. For task-focused instructions,
see the [how-to guides](../how-to/parse-and-build-headers.md); for the full API, the
[reference](../reference/headers.md).

## Headers are immutable value objects

Every header is a frozen dataclass whose fields are the *structured components* of the header —
`Age.seconds`, `ContentType.media_type`, `SetCookie.max_age`, and so on. Consequences:

- **Immutable.** You never mutate a header in place; you build a new one. This makes headers safe
  to share and cache.
- **Comparable and hashable.** Two headers are equal when their fields are equal, so headers work
  in sets and as dict keys.
- **The value is derived.** `.value` (and `str()`, `bytes()`) are computed from the fields, so the
  serialized form always reflects the current structured state — they can't drift apart.

## abnf drives parsing *and* validation

The library is built on [abnf](https://pypi.org/project/abnf/) grammars for the relevant RFCs.
Those grammars are used in both directions:

- **Parsing** — `Header.parse(value)` runs the grammar over the raw value and a visitor turns the
  parse tree into structured fields.
- **Validation** — the field types themselves (`Token`, `NonNegativeInt`, `EntityTag`, …) parse
  and validate on construction. So validity isn't a separate step bolted on; it's a property of
  the types the fields are made of.

A constructed header is therefore always well-formed: invalid input raises `ValueError` (or
`TypeError` for wrong argument types), whether it came from `parse()` or direct construction.

Because each field type is self-validating, a header is parsed **at most once**. `parse()` runs
the grammar and the visitor wraps the already-validated node text as leaf types with
`parse=False` (a trusted construction that skips re-parsing); direct construction validates only
the parts you actually pass. There is no second grammar pass to re-check a value the visitor just
built. Structured-Fields headers take this a step further: their serializer *is* the validator —
a value that would inject control characters or exceed a numeric bound simply fails to serialize —
so a successful serialization is grammar-valid by construction, with no re-parse at all.

## One construction contract

There is a single, consistent way to make headers:

- **`Header.parse(value)`** is the only string entry point.
- **Direct construction** takes the structured fields as their parsed types. Scalars coerce plain
  values (`Age(60)`); list-style headers take leaf types as varargs
  (`Connection(Token("keep-alive"), Token("close"))`); headers with richer values take value
  objects (`Upgrade(Protocol("HTTP", "2"))`). A raw string where a typed field is expected is a
  `TypeError` — reach for `parse()` instead.
- **Builders** (`ContentType.of(...)`, `SetCookie.build(...)`, `ETag.from_tag(...)`) exist only
  where piece-wise construction is richer than the stored fields.
- **`Header.create(name, value)`** dispatches by field name to the right subclass, or a
  `CustomHeader`.

This is a deliberate break from the older overloaded "string *or* pieces" constructors: one
object, one obvious way to build it, and precise types throughout.

## Shared bases where shapes repeat

Families that share an identical shape are factored onto a common base — dates (`DateHeader`),
entity-tag lists (`EntityTagListHeader`), product lists (`UserAgent`/`Server`), the auth pairs
(`WWWAuthenticate`/`ProxyAuthenticate`, …), and Structured-Fields lists/dictionaries. Where a
family only *rhymes* (different element types or separators), the headers stay individual — a
shared base isn't forced.

## Scope

Coverage spans the core HTTP RFCs (9110, 9111, 6265, 6266), widely-deployed extensions
(Forwarded, CORS, Link, HSTS, Alt-Svc, Prefer), and the modern Structured-Fields headers
(RFC 9651 and the specs built on it). Headers defined outside a clean RFC ABNF grammar are out of
scope, because the whole library is grammar-driven.

---

*Implementation notes, design decisions, and the migration history live in the project's internal
design document (`.claude/design/header-model.md`).*

# Design: HTTP headers as frozen dataclasses

**Status:** proposed · **Scope:** the ~34 `Header` subclasses in `src/http_headers/` and their base
**Decided:** stdlib dataclasses (not attrs); frozen/immutable; clean-break constructor API (`.parse()`)

## 1. Goals

- Represent each HTTP header as a **frozen `@dataclass`** whose fields are the structured
  components of the header (which are themselves already dataclasses/`str`/`int` subtypes).
- Use **abnf** for both directions:
  - **parsing** incoming header strings into structured fields (via the existing visitors);
  - **validation** of field values, via the self-validating field types (`ParsedStr` subclasses
    parse against an abnf `Rule` on construction).
- One **consistent, well-typed** construction and serialization contract across all headers,
  replacing the current per-class overloaded `__init__` + `value`-property idiom.

### Non-goals

- Rewriting the abnf grammars or the visitor layer. Visitors stay; component types stay
  (they become frozen where they are not already).
- Preserving the current constructor signatures. This is a **clean break** (the package is
  pre-1.0, `0.1.dev`).

## 2. Problems with the current design

Each header today: a class-level `name: str` + `visitor`, an **overloaded `__init__`** (raw
`value: str` *or* structured kwargs, different per class), and a `value` **property** whose
getter serializes and whose setter parses. Consequences:

- Every header reinvents constructor dispatch (`isinstance(value, str)` branching, ad-hoc
  `TypeError`/`ValueError`).
- The `value`-setter-assigns-instance-attrs pattern produced the 45 historical mypy
  "attribute already defined" errors and the `name = "age"` (str) vs base `FieldName` mismatch.
- Split identity: base compares `(name, value)` strings; some subclasses override to compare a
  component. No single equality story.
- Several latent falsy-`0` bugs (e.g. `if self.max_age` drops `max-age=0`; the Accept-Encoding
  / Accept-Charset `q=0` bugs already fixed).

## 3. Architecture

Three layers:

1. **`Header`** — an abstract base (not itself a dataclass) providing the shared interface and
   concrete presentation/registry behavior.
2. **Known headers** — one frozen dataclass per header, `name` as a `ClassVar`, structured
   fields, a `parse()` classmethod, and a derived `value` property.
3. **`CustomHeader`** — a frozen dataclass for arbitrary headers (e.g. `X-Request-Id`) that
   stores `name` and the raw value as fields.

### 3.1 Base `Header`

```python
from abc import ABC, abstractmethod
from typing import ClassVar, Self

from abnf import ParseError, Node, Rule

class Header(ABC):
    encoding: ClassVar[str] = "ISO-8859-1"
    rule: ClassVar[Rule]          # abnf rule for this header's value (subclass-provided)
    name: ClassVar[str]           # class constant on known headers; CustomHeader overrides
                                  # it with a per-instance property (one pyright-ignore there)

    # --- interface subclasses provide -------------------------------------
    @property
    @abstractmethod
    def value(self) -> str: ...    # serialized header body (no name)

    # parse(value) is a documented convention on known headers (not an abstractmethod,
    # because CustomHeader.parse takes (name, value) and would violate LSP).

    # --- shared presentation ----------------------------------------------
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"

    def __bytes__(self) -> bytes:
        return str(self).encode(self.encoding)

    @property
    def asgi_value(self) -> tuple[bytes, bytes]:
        return (self.name.encode("ascii"), self.value.encode("ascii"))

    # --- helper for subclass parse() --------------------------------------
    @classmethod
    def _node(cls, value: str) -> Node:
        """Parse `value` against cls.rule, translating ParseError to ValueError."""
        try:
            return cls.rule.parse_all(value)
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    # --- registry (unchanged behavior) ------------------------------------
    @classmethod
    def create(cls, name: str, value: str) -> "Header": ...
    @classmethod
    def subclass_tree(cls) -> "Iterable[type[Header]]": ...
```

Notes:
- **`name` is a `ClassVar[str]` on the base, not an abstract property.** (Pilot finding:
  pyright's `reportIncompatibleVariableOverride` rejects a `ClassVar` overriding an abstract
  property.) Known headers set `name: ClassVar[str] = "age"` — a compatible `ClassVar`-over-
  `ClassVar` override. `CustomHeader` needs a per-instance name, so it exposes `name` as a
  property backed by a field, carrying a single
  `# pyright: ignore[reportIncompatibleVariableOverride]`.
- `__eq__` takes a **position-only** `other` (`def __eq__(self, other, /)`) to stay compatible
  with legacy hand-written `__eq__(self, __o)` overrides during migration, and with
  `object.__eq__`.
- `_node()` centralizes the `ParseError -> ValueError` translation so each `parse()` is ~2 lines.
- `Header` is **not** a dataclass, so frozen dataclass subclasses inherit it without the
  "all dataclass bases must be frozen" constraint.

### 3.2 The known-header contract

```python
from dataclasses import dataclass
from typing import ClassVar
from abnf.grammars import rfc9111
from http_headers.parsedobjs import NonNegativeInt
from http_headers.visitors.rfc9111 import AgeVisitor

@dataclass(frozen=True)
class Age(Header):
    name: ClassVar[str] = "age"
    rule: ClassVar = rfc9111.Rule("Age")
    visitor: ClassVar = AgeVisitor()

    seconds: NonNegativeInt

    @classmethod
    def parse(cls, value: str) -> "Age":
        return cls(cls.visitor.visit(cls._node(value)))

    @property
    def value(self) -> str:
        return str(self.seconds)
```

- **Fields** are the structured data and the single source of truth.
- **`parse()`** is the only string entry point: `cls._node(value)` validates via abnf, the
  visitor produces structured data, `cls(...)` builds the instance.
- **`value`** is derived (read-only). There is no setter; instances are immutable.

## 4. Key design decisions

### 4.1 `name` / `rule` / `visitor` are `ClassVar`

Not dataclass fields — they are per-class constants. This removes them from `__init__`, `__eq__`,
and the field list, and fixes the base-class typing mismatch.

### 4.2 Collection fields are **tuples**, not lists

A frozen dataclass with a `list` field is *defined* as hashable but raises `TypeError` when
hashed (lists are unhashable). Since headers must remain hashable (they were, via
`hash((name, value))`) and immutable, all collection fields use tuples:

```python
directives: tuple[Token, ...]          # Connection
methods: tuple[Token, ...]             # Allow
codings: tuple[WeightedCoding, ...]    # Accept-Encoding
```

`parse()` builds tuples from the visitor's lists. For direct-construction ergonomics, a
`__post_init__` may coerce an incoming iterable to a tuple (see 4.3).

### 4.3 Validation and coercion

- **Validation** lives in the field types (`NonNegativeInt`, `Token`, `MediaType`, …), which
  parse/validate on construction against their abnf rule. The dataclass does not re-validate.
- **Coercion** at direct construction uses a small **custom `__init__` with widened parameter
  types**, not `__post_init__`. (Pilot finding: the dataclass-generated `__init__` types each
  parameter as the *field* type, so `Age(23)` — a plain `int` — is a type error against a
  `seconds: NonNegativeInt` field. A custom `__init__` typed `int` accepts the plain value,
  coerces it, and keeps the field's precise read type.)

  ```python
  seconds: NonNegativeInt              # precise read type: header.seconds is NonNegativeInt

  def __init__(self, seconds: int) -> None:
      object.__setattr__(self, "seconds", NonNegativeInt(seconds))   # frozen -> setattr
  ```

  Defining `__init__` in the class body suppresses dataclass's generated one (it keeps `eq`,
  `__hash__`, `repr` from the fields). Headers whose fields are always passed already-typed (via
  `parse()`) can skip the custom `__init__` and use the generated one. Note `__post_init__` is
  **not** called when a custom `__init__` is defined.

### 4.6 Do NOT use `@dataclass(slots=True)` on headers

`slots=True` makes the decorator **recreate the class**, which leaves the original,
pre-slots class lingering in `Header.__subclasses__()` (weakly referenced, GC-timing
dependent). `create()` walks `__subclasses__()` and can then pick up the **stale** class, so
`Header.create("host", …)` returns an instance of a *different* class object than direct
construction — and their strict-type `__eq__` returns `NotImplemented`/False. (Pilot finding in
step 5.) Slots also buy little here: the `Header` base isn't slotted, so instances keep a
`__dict__` regardless. All header dataclasses use plain `@dataclass(frozen=True)`.

### 4.4 Equality and hashing

Come free from `@dataclass(frozen=True)` (`eq=True` default → generated `__eq__` and `__hash__`).
This is a deliberate behavior change from the old `(name, value)`-string comparison:

- Equality is **strict same-type** and **field-by-field**. Field types with case-insensitive
  semantics (`CaselessMixin` on `Token`, `Filename`, …) contribute their own `__eq__`, so
  case-insensitivity is preserved where the field type provides it.
- Headers that previously hand-rolled `__eq__`/`__hash__` (e.g. `ETag` comparing `entity_tag`)
  no longer need to — the single-field dataclass eq is equivalent.

### 4.5 Custom headers

```python
from http_headers.visitors.rfc9110 import FieldName, FieldValue

@dataclass(frozen=True, slots=True)
class CustomHeader(Header):
    rule: ClassVar = rfc9110.Rule("field-value")

    name: FieldName        # instance field (validates as a token)
    _value: FieldValue

    @classmethod
    def parse(cls, name: str, value: str) -> "CustomHeader":
        return cls(FieldName(name), FieldValue(value))

    @property
    def value(self) -> str:
        return self._value
```

`Header.create(name, value)` looks up a known subclass by `name` (case-insensitive) and calls its
`parse(value)`; on no match it returns `CustomHeader.parse(name, value)`.

## 5. Header taxonomy → dataclass shape

| Category | Headers | Field shape |
|---|---|---|
| Scalar | `Age`, `ContentLength` | `seconds: NonNegativeInt` etc. |
| Date/time | `Date`, `Expires`, `LastModified`, `IfModifiedSince`, `IfUnmodifiedSince` | `date: datetime` |
| Scalar-or-date | `RetryAfter` | `delay: NonNegativeInt \| datetime` |
| Single string | `Host`, `Location` | `hostname: Host`, `port: int \| None` … |
| Token list | `Connection`, `Allow`, `Vary`, `ContentEncoding`, `AcceptRanges` | `tuple[Token, ...]` |
| Weighted list | `Accept`, `AcceptEncoding`, `AcceptCharset` | `tuple[WeightedCoding, ...]` |
| Composite single | `ContentType`, `ContentDisposition`, `ContentRange`, `ETag` | one component dataclass field |
| Entity-tag list | `IfMatch`, `IfNoneMatch` | `tuple[EntityTag, ...]` |
| Directive list | `CacheControl`, `AuthenticationInfo` | named fields + extension tuple |
| Auth | `Authorization`, `WWWAuthenticate` | credentials/challenge dataclass(es) |
| Cookie | `Cookie`, `SetCookie` | pair tuple / many attribute fields |

**Category bases — use only for *identical* shapes.** Where a whole family shares one shape,
factor a frozen-dataclass intermediate base holding the field(s), `parse()`, and `value`, so
each concrete header is just `name`/`rule`/`visitor` ClassVars (no `@dataclass` decorator needed
— it inherits the base's). `DateHeader` (step 3) is the model.

Do **not** force a shared base when the family only *rhymes*. The token-list family
(`Connection`, `Allow`, `Vary`, `ContentEncoding`, `AcceptRanges`, step 4) was left as five
individual dataclasses because they vary in element type (`Token`/`RangeUnit`/`FieldName`),
separator (`","` vs `", "`), and special-casing (`Vary` serializes empty as `*`). A generic
`ListHeader[T]` base also hits a hard limit: **a `ClassVar` cannot reference the class's
`TypeVar`**, so an `element` factory ClassVar typed with `T` doesn't type-check. Individual
~20-line dataclasses kept the semantic field names (`.methods`, `.directives`, …) and read
clearer than a parametrized base.

### 5.1 Common patterns

**Scalar / composite-single** — visitor returns the field directly:

```python
@classmethod
def parse(cls, value: str) -> "ETag":
    return cls(cls.visitor.visit(cls._node(value)))

@property
def value(self) -> str:
    return str(self.entity_tag)
```

**Token list** — visitor returns a list; store a tuple; join to serialize:

```python
methods: tuple[Token, ...]

@classmethod
def parse(cls, value: str) -> "Allow":
    return cls(tuple(cls.visitor.visit(cls._node(value))))

@property
def value(self) -> str:
    return ", ".join(self.methods)
```

**Directive list (`CacheControl`)** — drive both `parse` and `value` off a shared
`directive-name → field` mapping instead of a hand-written filter list (validated in the
prototype: 138 lines → ~70, and `s-maxage=0` now round-trips):

```python
_BOOL = {"immutable": "immutable", "public": "public", ...}
_INT  = {"max-age": "max_age", "s-maxage": "s_maxage", ...}
_BOOL_OR_STR = {"no-cache": "no_cache", "private": "private"}

@classmethod
def parse(cls, value: str) -> "CacheControl":
    kw, extension = {}, []
    for d in cls.visitor.visit(cls._node(value)):
        n = str(d.name)
        if   n in _BOOL:        kw[_BOOL[n]] = True
        elif n in _INT:         kw[_INT[n]] = d.value
        elif n in _BOOL_OR_STR: kw[_BOOL_OR_STR[n]] = d.value if isinstance(d.value, str) else True
        else:                   extension.append(d)
    return cls(**kw, cache_extension=tuple(extension))
```

## 6. Component types

The visitor-produced component types (`MediaType`, `AuthParam`, `WeightedCoding`, `ExtValue`,
`EntityTag`, `CacheDirective`, `RangeResp`, …) are already dataclasses. They become
`@dataclass(frozen=True)` for consistency and hashability; where they currently define a custom
`__init__` (e.g. `WeightedCoding`, `CacheDirective`) that logic moves to `__post_init__` /
converters or is expressed as normal fields. Collection members inside them likewise become
tuples.

## 7. Backward-incompatible changes

- **Construction**: `Age("23")` → `Age.parse("23")`; `Age(seconds=23)` → `Age(23)` (coerced) or
  `Age(NonNegativeInt(23))`. Same pattern for every header.
- **`value` is read-only** — no `header.value = ...`. Build a new instance instead (immutability).
- **Equality** is strict same-type, field-by-field (was `(name, value)` strings across
  subclasses).
- `Header.create(name, value)` and `subclass_tree()` keep their signatures/behavior.
- **Tests** that pass a raw string to a constructor migrate to `.parse()`; equality expectations
  built from the pieces migrate to the new field constructors. Every header module has a test
  module already, so coverage guides each conversion.

## 8. Rollout plan

Incremental, simple → complex, tests updated with each step; ruff + basedpyright + pytest green
at every step:

1. ✅ Base `Header` (ABC + helpers), `CustomHeader`, registry, and the `_node()` helper.
2. ✅ Scalar (`Age`, `ContentLength`) — establishes the pattern end to end.
3. ✅ Date family — shared `DateHeader` base (`dateheader.py`); each of `Date`, `Expires`,
   `LastModified`, `IfModifiedSince`, `IfUnmodifiedSince` is now pure ClassVar config
   (name/rule/visitor). `Expires`'s field standardized `expire_date` → `date`.
4. ✅ Token lists (`Connection`, `Allow`, `Vary`, `ContentEncoding`, `AcceptRanges`) — five
   individual dataclasses (varargs `__init__` coercing to `tuple`, `.parse()`, join `value`);
   fields renamed for consistency (`content_coding` → `codings`). See §5 on why no shared base.
5. ✅ Composite-single — `Location`, `Host`, `ETag`, `ContentRange`, `ContentType`
   (frozen-ified `MediaType` + `Parameter`; `ContentType.of(...)` builder; `ETag.from_tag(...)`;
   fixed a falsy-`0` bug in the ContentRange visitor), plus `ContentDisposition` (done later):
   `.build(type, parms)` / `.parse()`, params stored as a tuple of `FilenameParm`/`DispExtParm`;
   frozen-ified `ExtValue`/`FilenameParm`/`DispExtParm`. Aligned `build`'s filename detection
   with the parser (case-insensitive) — the old set-membership check silently misrouted
   uppercase `FILENAME` to a `DispExtParm`.
6. ✅ Weighted lists (`Accept`, `AcceptEncoding`, `AcceptCharset`) — frozen dataclasses with a
   tuple field + varargs `__init__`. Frozen-ified `WeightedCoding` and made `AcceptType`
   hashable (`params` → tuple, added `__hash__`). Fixed an `AcceptCharset` serialization bug
   that dropped charsets carrying no weight.
7. ✅ Entity-tag lists (`IfMatch`, `IfNoneMatch`) — shared `EntityTagListHeader` base
   (`entitytaglist.py`) holding `entity_tags: tuple[EntityTag, ...]` + a `wildcard` bool for
   `*`, with `parse()`/`value`; each subclass adds only name/rule/visitor and its own
   `matches()`. Second use of the category-base pattern (after `DateHeader`).
8. ✅ Directive lists (`CacheControl`, `AuthenticationInfo`). `CacheControl` lands the
   map-driven `parse`/`value` prototype (138 → ~110 lines, `s-maxage=0` preserved). Made
   `CacheDirective` hashable and fixed a latent bug where extension (unknown) directives never
   set `.value` (so `str()` crashed); made `AuthParam` frozen. Both headers now hashable.
9. ✅ Auth (`Authorization`, `WWWAuthenticate`). `Authorization` wraps a single credentials
   object; `WWWAuthenticate` a tuple of challenges (varargs init). Frozen-ified the four
   component types (`TokenCredentials`, `AuthParamCredentials`, `TokenChallenge`,
   `AuthParamChallenge`; the param ones store a tuple) so both headers hash.
10. ✅ Cookies (`Cookie`, `SetCookie`). `Cookie` is a tuple of `CookiePair` (already hashable).
    `SetCookie` splits its two old constructor modes cleanly: `.build(...)` validates piece-wise
    input (strict grammar), `.parse()` runs the lenient RFC 6265 section 5 algorithm; the
    dataclass `__init__` is the trusted internal constructor. `extension` is now a tuple, so the
    header hashes.
11. ✅ Final sweep. Caught two headers missed by the earlier steps — `RetryAfter`
    (`delay: NonNegativeInt | datetime`) and `UserAgent` (tuple of `Product`/`Comment`) — and
    migrated them (frozen-ified `Product`, fixing a falsy `__str__` bug that dropped a
    version-less product). Removed the now-dead legacy branch in `Header.create()` and declared
    a base `parse()` so `create()` is `subcls.parse(value)`; dropped the unused
    `CustomHeader.parse`. Frozen-ified the remaining active components (`MediaRange`,
    `RangeResp`, `UnsatisfiedRange`). Every header is a frozen dataclass and hashes.

Each numbered step is a self-contained commit.

**Not migrated:** `visitors/rfc9110/acceptlanguage.py` is an orphan — a complete
Accept-Language visitor with no header wrapping it. Left as-is; wrapping it in an
`AcceptLanguage` header (weighted-list shape) is a natural future addition.

## 9. Open questions / risks

- ~~**`Self` typing**~~ **Decided:** add `typing_extensions` as a runtime dependency and use
  `typing_extensions.Self` for `parse()` return types (3.10 has no `typing.Self`).
- ~~**Abstract `name` as property vs `ClassVar`**~~ **Resolved (step 2):** pyright rejects a
  `ClassVar` overriding an abstract property, so `name` is a `ClassVar[str]` on the base and
  `CustomHeader` overrides it with a property carrying one `reportIncompatibleVariableOverride`
  ignore. See §3.1.
- **`RetryAfter` union field** (`NonNegativeInt | datetime`) and **`Host`/`ContentRange`**
  multi-field serialization need per-header `value` logic — no shared shortcut.
- **`SetCookie`** is large (many optional attributes + cookie-date parsing); it may warrant its
  own sub-design when we reach step 10.
```

# http-headers — working notes for agents

A typed, immutable model of HTTP headers. Each header is a frozen dataclass that
parses/validates against an `abnf` grammar. Python >= 3.10.

## Gate (run before considering any change done)

```bash
uv run pytest -q          # tests
uv run ruff check .       # lint (rules: E, F, I, UP, B; E501 intentionally off)
uv run basedpyright       # types (standard mode)
```

All three must be clean. Prefer the dedicated tools over ad-hoc scripts.

## Workflow conventions

- **Test-first.** For a bug or new behavior, write a failing test, then make it pass.
- **Pre-release.** No git tags yet (hatch-vcs → dev version), so **API breaks are free** —
  don't preserve backward compatibility for its own sake; do update tests + docs.
- **Commits.** Concise subject; body explains the *why*. Keep the gate green per commit.
- **Docs live in `docs/`** (Sphinx + MyST). Design rationale: `docs/explanation/design.md`.

## The header model — invariants that bite if you don't know them

- **`Header.parse(value)` is the only string entry point.** Constructors take each field as
  its already-parsed type (a leaf type or value object), never a raw string. Passing a raw
  `str` where a typed field is expected raises `TypeError` pointing at `parse()`.
- **Frozen dataclasses; build with `object.__setattr__`** in a custom `__init__`.
- **No `slots=True` on `Header` subclasses** — it breaks the registry / `type()`-shadowing and
  the per-instance `value` cache. (`CookiePair` uses slots, but it is *not* a `Header`.)
- **Field types self-validate.** Leaf types subclass `ParsedStr` (`parsedobjs.py`) and parse
  against a grammar `Rule` in `__new__`. `LeafType(x, parse=False)` skips validation — the
  *trusted* path visitors use on already-parsed node text. `LeafType(existing_leaf)`
  short-circuits (isinstance), so coercing a leaf is a no-op.
- **Value objects coerce str→leaf** (the "MediaType pattern"): the field is typed as the leaf,
  the custom `__init__` takes `str` and wraps it. This is the validating composition layer;
  it is why `Protocol("HTTP", "2")` and `Host("example.com", 8080)` still accept strings.
- **Runtime field-type check** (annotation-driven, in `header.py`) enforces the construction
  contract two ways: `__init_subclass__` wraps a *custom* `__init__`; the base
  `Header.__post_init__` covers a *dataclass-generated* `__init__`. A subclass that overrides
  `__post_init__` MUST call `super().__post_init__()` (or it loses the check).
- **A header is parsed at most once.** Visitors build leaves with `parse=False`; constructors
  do not re-parse. Structured Fields headers instead validate by *serializing* (the serializer
  is the validator) — they force `self.value` in `__init__`, before the field check.
- **`value` is cached** per instance (`cached_property`, swapped in by `__init_subclass__`).
- **`abnf` drives every grammar** — except `structuredfields.py` (RFC 9651), whose serialize
  validation and value codec are hand-rolled. That is the main fuzz surface
  (`tests/test_structuredfields_properties.py`).

## Where things live

- Header classes: `src/http_headers/<name>.py` (usually one class each).
- Base class + field-check machinery: `src/http_headers/header.py`.
- Leaf-string bases: `src/http_headers/parsedobjs.py` (`ParsedStr`, `CaselessMixin`,
  `NonNegativeInt`).
- Visitors + value objects + leaf types: `src/http_headers/visitors/` (grouped by RFC).
- Structured Fields codec: `src/http_headers/structuredfields.py`; SF header bases:
  `structuredheaders.py`.
- Public surface (incl. leaf types re-exported for strict construction): `__init__.py`.
- Tests: `tests/` (one per header, plus `test_injection.py` and the property suite).

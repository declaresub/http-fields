# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project is in its 0.x series;
the API may still change between minor versions.

## [0.1.1] - 2026-07-22

Initial release published to PyPI as **http-fields** (`import http_fields`).

(`0.1.0` was tagged but never published to PyPI: its package metadata was missing a summary
and carried a `Development Status :: 5 - Production/Stable` classifier that overstated the
stability of a 0.x release. Caught on TestPyPI before the PyPI upload.)

### Added

- A typed, immutable model of HTTP header fields: each header is a frozen dataclass whose fields
  are the header's structured components, parsed and validated against the relevant RFC ABNF
  grammar — RFC 9110/9111, 6265, 6266, widely-deployed extensions (Forwarded, CORS, Link, HSTS,
  Alt-Svc, Prefer), and the RFC 9651 Structured Fields headers.
- **One construction contract.** `Header.parse(value)` is the only entry point that accepts a raw
  string; constructors take each field as its already-parsed type, so a constructor never re-runs
  the grammar on untrusted text. Passing a raw string where a typed field is expected raises
  `TypeError` pointing at `parse()`. Value objects (`Protocol`, `LinkValue`, `AltValue`,
  `ForwardedElement`, `Preference`, `Host`, …) accept plain strings for their individual parts and
  coerce them to validated leaf types.
- Self-validating leaf types, so an invalid value cannot be held at all: `Token`, `Method`,
  `FieldName`, `RangeUnit`, `LanguageTag`, `CorsMethod`/`CorsFieldName`, `Expectation`,
  `Hostname`, `ProtocolName`/`ProtocolVersion`, `ReceivedProtocol`/`ReceivedBy`/`Comment`,
  `URIReference`, `ProtocolId`/`AltAuthority`, and a shared optional-valued `Param`.
- An annotation-driven runtime field-type check on every header, applied uniformly with no
  per-class configuration.
- A standalone RFC 9651 Structured Fields implementation (Item / List / Dictionary).

### Security

- Every construction path — not just `parse()` — rejects CR/LF/NUL and other invalid content, so a
  header built from partially attacker-controlled data cannot be used for response splitting /
  header injection. `parse()` input is length-bounded to limit CPU exhaustion from pathological
  input.

### Performance

- A header is parsed **at most once**: visitors build field values as trusted leaf types, skipping
  a re-parse of text the grammar just validated. Structured-Fields headers validate by serializing
  rather than re-parsing.
- Each header's serialized `value` (and `str()`/`bytes()`/`asgi_value`) is computed once and cached
  per instance.

[0.1.1]: https://github.com/declaresub/http-fields/releases/tag/v0.1.1

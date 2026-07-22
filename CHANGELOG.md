# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project has not yet made a
tagged release; everything below is unreleased and the API may still change.

## [Unreleased]

### Changed

- **Breaking — strict typed construction.** `Header.parse(value)` is now the only entry point
  that accepts a raw string. Header constructors take each field as its already-parsed type, so a
  constructor never re-runs the grammar on untrusted text.
  - List-style headers take their leaf types as varargs instead of raw strings:
    `Connection`, `Allow`, `Vary`, `Trailer`, `Accept-Ranges`, `Content-Encoding`,
    `Content-Language`, and the CORS list headers (`Access-Control-Allow-Methods`,
    `-Allow-Headers`, `-Expose-Headers`, `-Request-Headers`). For example
    `Connection("keep-alive")` now raises `TypeError`; use `Connection(Token("keep-alive"))` or
    `Connection.parse("keep-alive")`.
  - Passing a raw string where a typed field is expected raises `TypeError`, with a message that
    points to the header's `parse()` method.
  - Value-object constructors (e.g. `Protocol`, `LinkValue`, `AltValue`, `ForwardedElement`,
    `Preference`, `Host`) still accept plain strings for their individual string parts and coerce
    them to validated leaf types, so `Host("example.com", 8080)` and
    `Upgrade(Protocol("HTTP", "2"))` are unchanged.

### Added

- Self-validating leaf types for previously plain string fields, so an invalid value can no
  longer be held by a value object: `ProtocolName`/`ProtocolVersion` (Upgrade),
  `ReceivedProtocol`/`ReceivedBy`/`Comment` (Via), `URIReference` (Link),
  `ProtocolId`/`AltAuthority` (Alt-Svc), `Hostname` (Host), and a shared optional-valued `Param`
  used by Link, Prefer, Alt-Svc, and Forwarded.
- Annotation-driven runtime field-type check: every header verifies each field matches its
  declared type on construction, uniformly and with no per-class configuration.

### Fixed

- **Security:** every construction path — not just `parse()` — now rejects CR/LF/NUL and other
  invalid content, so a header built from partially attacker-controlled data cannot be used for
  response splitting / header injection.

### Performance

- A header is now parsed **at most once.** The visitors build field values as trusted leaf types
  (skipping a re-parse of text the grammar just validated), and the previous re-parse in
  constructors has been removed. Structured-Fields headers (Cache-Status, Proxy-Status,
  Content-Digest, Repr-Digest, Cache-Control) validate by serializing rather than re-parsing.
- Each header's serialized `value` (and `str()`/`bytes()`/`asgi_value`) is computed once and
  cached per instance.

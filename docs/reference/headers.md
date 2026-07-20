# Header catalog

Every header class exported from `http_headers`, grouped by function. All are frozen dataclasses
sharing the same contract:

- `Header.parse(value)` — validate and parse a raw header value.
- direct construction from the header's fields (scalars coerce; list headers take varargs).
- `str()`, `bytes()`, `.value`, `.asgi_value` for output.
- immutable, comparable, hashable.

A handful expose extra constructors — see [Special constructors](#special-constructors) below.

## Content negotiation

| Header | Spec | Notes |
|---|---|---|
| `Accept` | RFC 9110 | media ranges with weights |
| `AcceptCharset` | RFC 9110 | charsets with weights |
| `AcceptEncoding` | RFC 9110 | content codings with weights |
| `AcceptLanguage` | RFC 9110 | language ranges with weights |
| `AcceptRanges` | RFC 9110 | supported range units |
| `Vary` | RFC 9110 | field names, or `*` |

## Representation metadata

| Header | Spec | Notes |
|---|---|---|
| `ContentType` | RFC 9110 | media type; builder `ContentType.of(...)` |
| `ContentEncoding` | RFC 9110 | content codings |
| `ContentLanguage` | RFC 9110 | language tags |
| `ContentLength` | RFC 9110 | `NonNegativeInt` |
| `ContentLocation` | RFC 9110 | a URI |
| `ContentRange` | RFC 9110 | range unit + positions |
| `ContentDisposition` | RFC 6266 | type + params; builder `ContentDisposition.build(...)` |

## Validators and conditionals

| Header | Spec | Notes |
|---|---|---|
| `ETag` | RFC 9110 | an entity-tag; builder `ETag.from_tag(tag, weak=False)` |
| `LastModified` | RFC 9110 | a `datetime` |
| `IfMatch` / `IfNoneMatch` | RFC 9110 | entity-tags, or `*` (`wildcard=True`) |
| `IfModifiedSince` / `IfUnmodifiedSince` | RFC 9110 | a `datetime` |
| `IfRange` | RFC 9110 | an `EntityTag` or `datetime` |

## Range requests

| Header | Spec | Notes |
|---|---|---|
| `Range` | RFC 9110 | range unit + `IntRange` / `SuffixRange` |

## Caching

| Header | Spec | Notes |
|---|---|---|
| `Age` | RFC 9111 | `NonNegativeInt` seconds |
| `CacheControl` | RFC 9111 | cache directives |
| `Expires` | RFC 9111 | a `datetime` |

## Authentication

| Header | Spec | Notes |
|---|---|---|
| `WWWAuthenticate` / `ProxyAuthenticate` | RFC 9110 | challenges |
| `Authorization` / `ProxyAuthorization` | RFC 9110 | credentials |
| `AuthenticationInfo` / `ProxyAuthenticationInfo` | RFC 9110 | auth-params |

## Cookies

| Header | Spec | Notes |
|---|---|---|
| `Cookie` | RFC 6265 | cookie pairs |
| `SetCookie` | RFC 6265 | builder `SetCookie.build(...)`; lenient `SetCookie.parse(...)` |

## Connection management

| Header | Spec | Notes |
|---|---|---|
| `Host` | RFC 9110 | hostname + optional port |
| `Connection` | RFC 9110 | connection options |
| `Upgrade` | RFC 9110 | protocols |
| `Via` | RFC 9110 | intermediaries |
| `Trailer` | RFC 9110 | field names |
| `TE` | RFC 9110 | transfer codings with weights |
| `MaxForwards` | RFC 9110 | `NonNegativeInt` |

## Request context

| Header | Spec | Notes |
|---|---|---|
| `From` | RFC 9110 | a mailbox |
| `Referer` | RFC 9110 | a URI |
| `UserAgent` | RFC 9110 | products / comments |
| `Expect` | RFC 9110 | expectations (usually `100-continue`) |

## Response context

| Header | Spec | Notes |
|---|---|---|
| `Allow` | RFC 9110 | methods |
| `Date` | RFC 9110 | a `datetime` |
| `Location` | RFC 9110 | a URI |
| `RetryAfter` | RFC 9110 | `NonNegativeInt` or `datetime` |
| `Server` | RFC 9110 | products / comments |

## CORS / Fetch

| Header | Spec | Notes |
|---|---|---|
| `Origin` | RFC 6454 / Fetch | an origin |
| `AccessControlAllowOrigin` | Fetch | origin, `null`, or `*` |
| `AccessControlAllowCredentials` | Fetch | always `true` |
| `AccessControlAllowMethods` | Fetch | methods |
| `AccessControlAllowHeaders` / `AccessControlExposeHeaders` / `AccessControlRequestHeaders` | Fetch | field names |
| `AccessControlMaxAge` | Fetch | `NonNegativeInt` |
| `AccessControlRequestMethod` | Fetch | a single method |

## Other extensions

| Header | Spec | Notes |
|---|---|---|
| `Forwarded` | RFC 7239 | forwarding elements |
| `Link` | RFC 8288 | link values |
| `StrictTransportSecurity` | RFC 6797 | `max_age` + `include_subdomains` / `preload` |
| `AltSvc` / `AltUsed` | RFC 7838 | alternative services (`clear=True` for `clear`) |
| `Prefer` / `PreferenceApplied` | RFC 7240 | preferences |

## Structured Fields (RFC 9651)

See also [Work with Structured Fields](../how-to/structured-fields.md).

| Header | Spec | Notes |
|---|---|---|
| `Priority` | RFC 9218 | `urgency` (0-7) + `incremental` |
| `CacheStatus` | RFC 9211 | SF List of cache entries |
| `ProxyStatus` | RFC 9209 | SF List of intermediaries |
| `ContentDigest` / `ReprDigest` | RFC 9530 | SF Dictionary of algorithm → digest |

## Generic

| Header | Notes |
|---|---|
| `CustomHeader` | any header with an arbitrary field name; `CustomHeader(name, value)` |

## Special constructors

Beyond `.parse()` and direct construction:

| Header | Constructor |
|---|---|
| `ContentType` | `ContentType.of(type, subtype, *, charset=None, boundary=None, params=None)` |
| `SetCookie` | `SetCookie.build(cookie_name, cookie_value, *, domain=None, path=None, expires=None, max_age=None, secure=False, http_only=False, samesite="Lax", extension=None)` |
| `ContentDisposition` | `ContentDisposition.build(disposition_type, disposition_parms=None)` |
| `ETag` | `ETag.from_tag(tag, weak=False)` |
| `IfMatch`, `IfNoneMatch` | `IfMatch(*entity_tags, wildcard=False)` |
| `AltSvc` | `AltSvc(*values, clear=False)` |

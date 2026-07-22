# Code review findings — `http-fields`

Adversarial bug-finding review (2026-07-21). All 105 files under `src/http_fields/`
reviewed; findings below reproduced by execution unless marked *plausible*. Baseline at
review time: `uv run pytest -q` → 473 passed.

Status legend: ⬜ open · ✅ fixed (test added first, then fix).

---

## Confirmed (reproduced by execution)

### 🔴 Critical

- ✅ **1. Cookie `Expires` on the hour silently dropped.** `setcookie.py:107`
  (`CookieDateVisitor.visit_hms_time`). `filter(None, …)` eats time fields equal to `0`, so
  `00:00:00` / `10:00:05` raise `ValueError`, and `_parse_value` drops the whole `Expires`.
  Repro: `SetCookie.parse("a=b; Expires=Wed, 09 Jun 2021 10:00:05 GMT").expires` → `None`.
  Fix: filter on `is not None`.

### 🟠 High

- ✅ **2. `SetCookie.parse` crashes** on `"foo"` (no `=`) and `Domain=`/`Path=` (empty value).
  `setcookie.py:351,384`. `IndexError`. Fix: handle missing `=`; guard empty `attr_value`.
- ✅ **3. `Cookie.parse("a=")` crashes** on empty cookie value. `visitors/rfc6265.py:58`.
  `filter(None, …)` drops `""`. Fix: filter on `is not None`.
- ✅ **4. `ContentDisposition.value` emits dataclass repr** for ext parameters.
  `visitors/rfc6266.py:157` (`DispExtParm` lacks `__str__`). Fix: add `__str__`.
- ✅ **5. RFC 5987 ext-values percent-decoded twice.** `visitors/rfc6266.py:55`. `%2541.txt`
  → `A.txt` (should be `%41.txt`). Fix: decode once.
- ✅ **6. `Comment.__str__` doesn't re-escape** → User-Agent/Server/Via round-trip unparseable.
  `visitors/rfc9110/comment.py:12`. Fix: escape `\ ( )` in string items.
- ✅ **7. `ETag.parse('""')` / `W/""` crash** on empty entity-tags.
  `visitors/rfc9110/entitytag.py:46`. `IndexError` / `TypeError`. Affects ETag, IfMatch,
  IfNoneMatch, IfRange. Fix: filter on `is not None`; detect weak flag by type.
- ✅ **8. Dates ignore tzinfo.** `visitors/rfc9110/_base.py:34` (`imf_fixdate`). Non-UTC
  datetimes serialize the wrong instant. Fix: `astimezone(utc)` before formatting.
- ✅ **9. `CacheControl.parse("max-stale")` crashes.** `visitors/rfc9111.py:26`. Bare
  `max-stale` is valid; `NonNegativeInt(None)` → `TypeError`. Fix: allow valueless directive.
- ✅ **10. `]` stripped from cookie names/values** (typo `strip(" \t]")`). `setcookie.py:353,366`.
  `a=[v]` → `[v`. Fix: `strip(" \t")`.

### 🟡 Medium

- ✅ **11. `Host.parse(":80")` / `""` / `"host:"` break.** `visitors/rfc9110/host.py:5`;
  `host.py:33`. Fix: match children by node name; keep empty host `""`, empty port `None`.
- ✅ **12. SF serializer does no validation** — emits unparseable output (non-ASCII strings,
  invalid tokens/keys, 16-digit ints). `structuredfields.py:253`. Fix: validate per RFC 9651 §4.1.
- ✅ **13. `DigestHeader.parse` silently drops** non-binary members and parameters.
  `structuredheaders.py:57`. Fix: raise on non-binary, or preserve.
- ✅ **14. `Range.parse` drops `other-range`** and can serialize invalid `bytes=`.
  `visitors/rfc9110/range.py:70`; `range.py:36`. Fix: carry other-range as string or reject.
- ✅ **15. `Accept.parse('…;q="0.5"')` crashes**; out-of-range `q=5` silently clamped.
  `visitors/rfc9110/accept.py:92` (also `te.py:62`). Fix: strip quotes / catch; validate range.
- ✅ **16. HSTS crashes on quoted `max-age`**; missing `max-age` wrongly parses as `0`.
  `stricttransportsecurity.py:44`. Fix: strip DQUOTEs; raise if no `max-age`.
- ✅ **17. `asgi_value` uses ASCII but class encoding is latin-1.** `header.py:42`. obs-text
  crashes only on ASGI path. Fix: encode with `self.encoding`.
- ✅ **18. `SetCookie` round-trip invents `SameSite=Lax`** / emits invalid `SameSite=Default`.
  `setcookie.py:270,397`. Fix: track SameSite-absent as `None`; never serialize `Default`.
- ✅ **19. Cookie quoted values lose their `"`** on round-trip. `visitors/rfc6265.py:44`.
  Fix: preserve raw cookie-value node text.
- ✅ **20. Cookie names compare case-insensitively** (RFC 6265 is case-sensitive).
  `visitors/rfc6265.py:7` (`CaselessMixin`). Fix: drop `CaselessMixin`.
- ✅ **21. `Host` equality case-sensitive** (host names aren't). `host.py:25`. Fix: casefold hostname.
- ✅ **22. SF keeps duplicate keys** (RFC requires last-wins). `structuredfields.py:177,222`.
  Fix: de-dup keeping last occurrence.
- ✅ **23. ext-value doesn't percent-encode `/`** → unparseable Content-Disposition.
  `visitors/rfc6266.py:45`. Fix: `quote(..., safe="")`.

### ⚪ Low

- ✅ **24. `NonNegativeInt` truncates floats** — `Age(3.7)` → `"3"`. `parsedobjs.py:48`.
  Fix: reject non-integral. Also: `Allow("GET")==Allow("get")` (methods case-sensitive);
  `Host(host, 0)` drops port 0; SF unpadded base64 raises raw `binascii.Error`; naive-datetime
  SF uses local tz; `IntRange(500, 100)` accepted (last-pos < first-pos).

---

## Plausible (reasoned, not proven) — all resolved

- ✅ **P1.** `BareItem`/`Parameters`/`Member` are plain strings, not `TypeAlias`. `structuredfields.py:50`.
  Fix: real `TypeAlias` unions.
- ✅ **P2.** `ContentType.charset` returns the quoted form. `contenttype.py:70`. Fix: unquote in
  the `charset`/`boundary` accessors.
- ✅ **P3.** `Comment` is mutable yet hashed. `visitors/rfc9110/comment.py:9`. Fix: store `items`
  as a tuple.
- ✅ **P4.** `Date2Visitor` uses deprecated `datetime.utcnow()`. `visitors/rfc9110/httpdate.py:72`.
  Fix: `datetime.now(timezone.utc)`.
- ✅ **P5.** `transform()` is recursive — RecursionError DoS on long `Accept-*`.
  `visitors/rfc9110/_base.py:12`. Fix: rewritten iteratively.
- ✅ **P6.** `imf_fixdate` `%02d` for year — <1000 serializes <4 digits. `_base.py:54`.
  Fix: `%04d`.

---

## Systemic root causes

1. **`filter(None, …)` over visited children** eats falsy-but-valid `0`/`""`/time fields
   (#1, #3, #7, #11, #19). Fix pattern: filter on `is not None`, or match by `node.name`.
2. **Serializers trust their inputs** — `.value`/`__str__` never re-escape/re-validate, so
   `parse(x).value` can be unparseable (#4, #6, #12, #14, #18, #23). A property test
   `parse(h.value) == h` across all headers would catch most of these.
   Added as `tests/test_roundtrip.py` (one sample per concrete header + a coverage test
   that fails if a new header is added without a sample).

---

## Round 2 (Opus, scoped to the fixes + under-reviewed modules) — 3 new, all fixed

- ✅ **R2-1 (Med).** `SetCookie` with `SameSite=None` fabricated a `Secure` attribute on
  serialization, breaking `parse(h.value) == h`. `setcookie.py:280`. Fix: serialize `Secure`
  only when `self.secure`. (Regression introduced by #18.)
- ✅ **R2-2 (Low).** `StrictTransportSecurity.parse("max-age")` (valueless directive) hit
  `int("")`. Already raised `ValueError` (correct type) but with a leaky message; now routed
  through the clean "requires a max-age directive" error. `stricttransportsecurity.py:72`.
  (Gap in #16.)
- ✅ **R2-3 (Low).** `auth-scheme` compared case-sensitively; RFC 9110 §11.1 makes it
  case-insensitive (`Authorization.parse("Basic x") != Authorization.parse("basic x")`).
  `visitors/rfc9110/authscheme.py:7`. Fix: `AuthScheme(CaselessMixin, ParsedStr)`. Affects
  Authorization/Proxy-Authorization/WWW-Authenticate/Proxy-Authenticate.

Reviewer confirmed the SF value model, the auth family, Via/Upgrade/Forwarded/Alt-Svc/Link/
Prefer/Content-Range, and the round-1 fixes otherwise held up under edge-case fuzzing.

---

## Security review (Opus) — all remediated

Defensive review of the parser handling untrusted input.

- ✅ **S1 (Critical).** Response-splitting / header injection: every constructor (not
  just `parse()`) stored raw strings and emitted CR/LF/NUL into `bytes()`/`asgi_value`.
  Fix: `Header._validate_value()` re-parses the serialized value against the header
  grammar at construction; applied comprehensively (an empirical probe found every gap —
  UriHeader, Origin, CORS, Host, Expect, SetCookie, AltUsed, From, AltSvc, Forwarded,
  Link, Via, Prefer, TE, Upgrade, the SF list/digest bases, CacheControl). SetCookie
  (lenient parse) rejects control chars in its string fields instead.
- ✅ **S2 (High).** Super-linear parse-time DoS with no input bound. Fix: `max_length`
  ClassVar (default 8192), enforced by `_check_length` in `_node`/`_prefixed_node` and the
  SF/Priority/Content-Disposition/SetCookie parse paths; overridable per subclass.
- ✅ **S3 (Low).** `SetCookie.build(extension=…)` raised `abnf.ParseError`; now `ValueError`.

Approach note: chose construction-time validation over a serialization-boundary guard, so
the guarantee comes from the constructors (`X(str)` accepts exactly what `X.parse(str)`
does) rather than from `str()`/`bytes()`/`asgi_value` being able to raise.

Verified: the original review's repros (Location/CORS/Host/Origin injection, oversized
Accept, bad SetCookie extension) all raise ValueError; valid construction unaffected.

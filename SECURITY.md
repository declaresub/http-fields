# Security Policy

`http-fields` parses and validates HTTP header values, often from untrusted input, so
correctness of that validation is a security property (e.g. rejecting CR/LF/NUL to prevent
response splitting / header injection).

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**, not via a public issue:

- Preferred: GitHub's **"Report a vulnerability"** button on the repository's *Security* tab
  (private vulnerability reporting).
- Alternatively, email the maintainer at **charles@declaresub.com**.

Please include a description, affected version/commit, and a minimal reproduction. You'll get
an acknowledgement, and we'll coordinate a fix and disclosure with you.

## Supported versions

This project is in its 0.x series. Security fixes land on the latest released version, so please
confirm the issue against the newest `0.x` release before reporting.

| Version | Supported                                                     |
| ------- | ------------------------------------------------------------- |
| 0.1.x   | ✅                                                            |
| 0.1.0   | ❌ — tagged but never published to PyPI; use 0.1.1 or later    |

## Verifying a release

Releases are built and published by a GitHub Actions workflow
([`publish.yml`](.github/workflows/publish.yml)) from a signed tag, using **trusted publishing**
(OIDC — there are no long-lived PyPI API tokens that could be stolen). Both publish steps require
a manual approval in a protected environment. Every release is independently verifiable —
substitute the version you are checking for `0.1.1` below.

### PyPI attestations (PEP 740)

Artifacts on PyPI carry attestations binding them to this repository and workflow:

```sh
pip download --no-deps http-fields==0.1.1
uvx pypi-attestations verify pypi \
  --repository https://github.com/declaresub/http-fields \
  http_fields-0.1.1-py3-none-any.whl
```

The provenance can also be inspected directly:
<https://pypi.org/integrity/http-fields/0.1.1/http_fields-0.1.1-py3-none-any.whl/provenance>

It should name the publisher as repository `declaresub/http-fields`, workflow `publish.yml`,
environment `pypi`.

### Sigstore bundles

Each GitHub release attaches the wheel and sdist together with a `.sigstore.json` bundle:

```sh
gh release download v0.1.1 --repo declaresub/http-fields
uvx sigstore verify identity \
  --cert-identity "https://github.com/declaresub/http-fields/.github/workflows/publish.yml@refs/tags/v0.1.1" \
  --cert-oidc-issuer "https://token.actions.githubusercontent.com" \
  http_fields-0.1.1-py3-none-any.whl http_fields-0.1.1.tar.gz
```

### SBOM

Each release also attaches a CycloneDX SBOM (`http-fields.cdx.json`) describing the package's
runtime dependency closure (build and development tooling are excluded).

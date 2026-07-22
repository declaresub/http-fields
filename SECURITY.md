# Security Policy

`http-headers` parses and validates HTTP header values, often from untrusted input, so
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

This project is **pre-release** (no tagged release yet); the latest `master` is the supported
version. Once releases are published, this section will list the supported release lines.

## Verifying a release

Once releases are published to PyPI, this section will describe how to verify a release's
provenance (build attestations / Sigstore bundle and the attached SBOM).

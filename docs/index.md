# http-headers documentation

```{toctree}
:hidden:
:maxdepth: 2

tutorials/getting-started
how-to/parse-and-build-headers
how-to/custom-and-unknown-headers
how-to/structured-fields
reference/headers
reference/structured-fields
reference/api
explanation/design
```

`http-headers` represents HTTP headers as immutable Python dataclasses. [abnf](https://pypi.org/project/abnf/)
grammars drive both directions: **parsing** incoming header strings and **validating** field
values, so a constructed header is always well-formed.

Requires Python 3.10+.

## Documentation

The docs follow the [Diátaxis](https://diataxis.fr/) model:

- **[Tutorials](tutorials/getting-started.md)** — start here if you're new. A hands-on walk
  through installing, parsing, building, and serializing headers.
- **How-to guides** — task-focused recipes:
  - [Parse and build headers](how-to/parse-and-build-headers.md)
  - [Custom and unknown headers](how-to/custom-and-unknown-headers.md)
  - [Work with Structured Fields](how-to/structured-fields.md)
- **Reference** — precise technical description:
  - [Header catalog](reference/headers.md) — every header, grouped by spec, with its constructors.
  - [`structuredfields` API](reference/structured-fields.md)
- **[Explanation](explanation/design.md)** — the *why*: the frozen-dataclass model, the
  construction contract, and where validation lives.

## Install

```sh
uv add http-headers
# or: pip install http-headers
```

# http-fields

[![PyPI](https://img.shields.io/pypi/v/http-fields)](https://pypi.org/project/http-fields/)
[![Python versions](https://img.shields.io/pypi/pyversions/http-fields)](https://pypi.org/project/http-fields/)
[![CI](https://github.com/declaresub/http-fields/actions/workflows/ci.yml/badge.svg)](https://github.com/declaresub/http-fields/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/http-fields/badge/?version=latest)](https://http-fields.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/http-fields)](LICENSE.txt)

Typed, validated HTTP headers for Python. Each header is an immutable
[dataclass](https://docs.python.org/3/library/dataclasses.html) whose fields are the structured
components of the header. [abnf](https://pypi.org/project/abnf/) grammars are used both to
**parse** incoming header strings and to **validate** field values, so a constructed header is
always well-formed.

Requires Python 3.10+.

```python
from http_fields import ContentType, Header

ct = ContentType.parse("text/html; charset=UTF-8")
ct.type, ct.subtype, ct.charset          # ('text', 'html', 'UTF-8')
str(ct)                                   # 'Content-Type: text/html;charset=UTF-8'

ContentType.of(type="text", subtype="html", charset="utf-8")   # build from pieces
Header.create("x-request-id", "abc123")                         # dispatch by name
```

## Install

```sh
uv add http-fields
# or: pip install http-fields
```

## Documentation

Full documentation: **<https://http-fields.readthedocs.io/>**

It follows the [Diátaxis](https://diataxis.fr/) model:

- **Tutorial:**
  [Getting started](https://http-fields.readthedocs.io/en/latest/tutorials/getting-started.html)
- **How-to guides:**
  [parse & build](https://http-fields.readthedocs.io/en/latest/how-to/parse-and-build-headers.html) ·
  [custom / unknown headers](https://http-fields.readthedocs.io/en/latest/how-to/custom-and-unknown-headers.html) ·
  [Structured Fields](https://http-fields.readthedocs.io/en/latest/how-to/structured-fields.html)
- **Reference:**
  [header catalog](https://http-fields.readthedocs.io/en/latest/reference/headers.html) ·
  [`structuredfields` API](https://http-fields.readthedocs.io/en/latest/reference/structured-fields.html)
- **Explanation:**
  [the header model](https://http-fields.readthedocs.io/en/latest/explanation/design.html)

The sources live in [`docs/`](docs/index.md).

## Development

```sh
uv sync                       # create the environment
uv run pytest                 # run the tests
uv run ruff check .           # lint
uv run ruff format .          # format
uv run basedpyright           # type-check

uv sync --group docs          # add the docs toolchain
uv run sphinx-build -b html docs docs/_build/html   # build the docs locally
```

# http-headers

Typed, validated HTTP headers for Python. Each header is an immutable
[dataclass](https://docs.python.org/3/library/dataclasses.html) whose fields are the structured
components of the header. [abnf](https://pypi.org/project/abnf/) grammars are used both to
**parse** incoming header strings and to **validate** field values, so a constructed header is
always well-formed.

Requires Python 3.10+.

```python
from http_headers import ContentType, Header

ct = ContentType.parse("text/html; charset=UTF-8")
ct.type, ct.subtype, ct.charset          # ('text', 'html', 'UTF-8')
str(ct)                                   # 'Content-Type: text/html;charset=UTF-8'

ContentType.of(type="text", subtype="html", charset="utf-8")   # build from pieces
Header.create("x-request-id", "abc123")                         # dispatch by name
```

## Install

```sh
uv add http-headers
# or: pip install http-headers
```

## Documentation

Full documentation lives in [`docs/`](docs/index.md) and follows the
[Diátaxis](https://diataxis.fr/) model:

- **Tutorial:** [Getting started](docs/tutorials/getting-started.md)
- **How-to guides:** [parse & build](docs/how-to/parse-and-build-headers.md) ·
  [custom / unknown headers](docs/how-to/custom-and-unknown-headers.md) ·
  [Structured Fields](docs/how-to/structured-fields.md)
- **Reference:** [header catalog](docs/reference/headers.md) ·
  [`structuredfields` API](docs/reference/structured-fields.md)
- **Explanation:** [the header model](docs/explanation/design.md)

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

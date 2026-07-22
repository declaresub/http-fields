.PHONY: check test lint types fmt cov docs

# Run the full gate (must be clean before a change is done).
check: lint types test

test:
	uv run pytest -q

lint:
	uv run ruff check .

types:
	uv run basedpyright

# Auto-fix: format, then apply safe lint fixes.
fmt:
	uv run ruff format .
	uv run ruff check --fix .

cov:
	uv run pytest -q --cov=http_headers --cov-report=term-missing

docs:
	uv run sphinx-build -b html docs docs/_build/html

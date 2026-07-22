# Sphinx configuration. Prose lives in Markdown; MyST-Parser reads it directly.
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

project = "http-fields"
author = "Charles Yeomans"
copyright = "Charles Yeomans"  # noqa: A001

try:
    release = _version("http-fields")
except PackageNotFoundError:  # not installed in the docs environment
    release = "0.0.0"
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

# autodoc
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"  # render annotations into the field list
python_use_unqualified_type_names = True

# Cross-link stdlib types (datetime, Decimal, ...) in signatures.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Resolve [text](other.md) cross-links between source files, and allow the
# ::: fenced form for directives in addition to the ``` form.
myst_enable_extensions = ["colon_fence"]

# Generate anchors for h1-h3 so in-page links like [x](#some-heading) resolve.
myst_heading_anchors = 3

source_suffix = {".md": "markdown"}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "http-fields"

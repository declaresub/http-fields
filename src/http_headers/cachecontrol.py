"""CacheControl header class"""

import itertools

from abnf.grammars import rfc9111

from http_headers.header import Header
from http_headers.visitors.rfc9111 import CacheControlVisitor, CacheDirective


class CacheControl(Header):  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Cache-Control header."""

    name = "Cache-Control"

    def __init__(
        self,
        value: str | None = None,
        *,
        immutable: bool = False,
        max_age: int | None = None,
        max_stale: int | None = None,
        min_fresh: int | None = None,
        must_revalidate: bool = False,
        no_cache: bool | str | None = None,
        no_store: bool = False,
        no_transform: bool = False,
        only_if_cached: bool = False,
        private: bool | str | None = None,
        proxy_revalidate: bool = False,
        public: bool = False,
        s_maxage: int | None = None,
        cache_extension: list[CacheDirective] | None = None,
    ):
        """Initializes a Cache-Control header object.

        :param public: if True, then a public directive is added to header.
        :param private: if value is True, a private directive is added to header.  If value is a
            str or an iterable returning such, field names are included with the directive.
        :param no_cache: if value is True, a no-cache directive is added to header.  If value is a
            str or an iterable returning such, field names are included with the directive.
        :param no_store: if True, then a no-store directive is added to header.
        :param no_transform: if True, then a no-transform directive is added to header.
        :param must_revalidate: if True, then a no-revalidate directive is added to header.
        :param max_age: if an integer, then a max-age directive is added to header.
        :param s_maxage: if an integer, then a s-maxage directive is added to header.
        :param cache_extension: additional named arguments from which to generate directives.
        :rvalue: Header object

        """

        if value:
            self.value = value
        else:
            self.immutable = immutable
            self.public = public
            self.private = private
            self.no_cache = no_cache
            self.no_store = no_store
            self.no_transform = no_transform
            self.must_revalidate = must_revalidate
            self.proxy_revalidate = proxy_revalidate
            self.max_age = int(max_age) if max_age is not None else None
            self.max_stale = int(max_stale) if max_stale is not None else None
            self.min_fresh = int(min_fresh) if min_fresh is not None else None
            self.only_if_cached = only_if_cached
            self.s_maxage = int(s_maxage) if s_maxage is not None else None
            self.cache_extension = list(cache_extension) if cache_extension else []

    @property
    def value(self):
        directives = itertools.chain(
            filter(
                None,
                [
                    CacheDirective("immutable") if self.immutable else None,
                    CacheDirective("public") if self.public else None,
                    CacheDirective("private", self.private)
                    if isinstance(self.private, str)
                    else CacheDirective("private")
                    if self.private
                    else None,
                    CacheDirective("no-cache", self.no_cache)
                    if isinstance(self.no_cache, str)
                    else CacheDirective("no-cache")
                    if self.no_cache
                    else None,
                    CacheDirective("no-store") if self.no_store else None,
                    CacheDirective("no-transform") if self.no_transform else None,
                    CacheDirective("must-revalidate") if self.must_revalidate else None,
                    CacheDirective("proxy-revalidate")
                    if self.proxy_revalidate
                    else None,
                    CacheDirective("max-age", self.max_age) if self.max_age else None,
                    CacheDirective("max-stale", self.max_stale)
                    if self.max_stale
                    else None,
                    CacheDirective("min-fresh", self.min_fresh)
                    if self.min_fresh
                    else None,
                    CacheDirective("only-if-cached") if self.only_if_cached else None,
                    CacheDirective("s-max-age", self.s_maxage)
                    if self.s_maxage
                    else None,
                ],
            ),
            self.cache_extension,
        )
        return ",".join(str(directive) for directive in directives)

    @value.setter
    def value(self, val: str):
        standard_keys = {
            "immutable": "immutable",
            "public": "public",
            "private": "private",
            "no-cache": "no_cache",
            "no-store": "no_store",
            "no-transform": "no_transform",
            "must-revalidate": "must_revalidate",
            "proxy-revalidate": "proxy_revalidate",
            "max-age": "max_age",
            "max-stale": "max_stale",
            "min-fresh": "min_fresh",
            "only-if-cached": "only_if_cached",
            "s-max-age": "s_max_age",
        }
        cache_extension: list[CacheDirective] = []
        node = rfc9111.Rule("Cache-Control").parse_all(val)
        visitor = CacheControlVisitor()
        directives: list[CacheDirective] = visitor.visit(node)
        for directive in directives:
            if directive.name in standard_keys:
                setattr(self, standard_keys[directive.name], directive.value)
            else:
                cache_extension.append(directive)
        self.cache_extension = cache_extension

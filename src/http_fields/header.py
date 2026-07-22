"""HTTP header abstract base class and the generic custom-header class."""

from __future__ import annotations

import dataclasses
import inspect
import types
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cached_property, wraps
from typing import Any, ClassVar, Union, get_args, get_origin

from abnf import Node, ParseError, Rule
from abnf.grammars import rfc9110

from http_fields.visitors.rfc9110 import FieldName, FieldValue


def _matches_type(value: object, hint: object) -> bool:
    """A small, deterministic runtime type check covering the field-annotation shapes
    headers actually use: a concrete type, ``tuple[X, ...]``/``tuple[X, Y]``, unions
    (``X | Y``, ``Optional``), and ``None``. Every element is checked (no sampling).
    Unrecognised shapes are not blocked."""
    origin = get_origin(hint)
    if origin is tuple:
        args = get_args(hint)
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:  # tuple[X, ...]
            return all(_matches_type(v, args[0]) for v in value)
        return len(value) == len(args) and all(
            _matches_type(v, a) for v, a in zip(value, args, strict=True)
        )
    if origin is Union or origin is types.UnionType:
        return any(_matches_type(value, a) for a in get_args(hint))
    if hint is type(None):
        return value is None
    if isinstance(hint, type):
        return isinstance(value, hint)
    return True  # unrecognised annotation shape: don't block


class Header(ABC):
    """Abstract base for HTTP headers.

    Known headers are frozen dataclasses whose fields are the structured components of the
    header value. Each sets ``name`` (and usually ``rule``/``visitor``) as a ClassVar,
    implements a ``parse(value)`` classmethod, and exposes a derived ``value`` property.
    Arbitrary headers (e.g. ``X-Request-Id``) are represented by :class:`CustomHeader`.
    """

    encoding: ClassVar[str] = "ISO-8859-1"
    rule: ClassVar[Rule]  # abnf rule for the header value; provided by subclasses
    name: ClassVar[str]  # field name; a class constant on known headers,
    # overridden by a per-instance property on CustomHeader.
    # Maximum accepted length of a value passed to parse(). Parsing is super-linear
    # in the length for some grammars, so an oversized value is a CPU-exhaustion
    # vector; reject it up front. Override per subclass where larger values are
    # legitimate (e.g. cookie-heavy deployments).
    max_length: ClassVar[int] = 8192
    # Per-class cache of resolved field-annotation hints (populated on first use).
    _field_hints_cache: ClassVar[dict[str, object] | None] = None

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # Headers (and every value-object they hold) are immutable, so the serialized
        # value is stable: cache it per instance with functools.cached_property, so it
        # is computed at most once (str/bytes/asgi_value/__eq__/__hash__ and direct
        # access all share it). We swap the descriptor in here, at class creation,
        # rather than decorating each subclass's `value` -- a cached_property directly
        # overriding the abstract `value` property trips reportIncompatibleMethodOverride,
        # so subclasses keep a plain @property. cached_property writes to the instance
        # __dict__, bypassing the frozen __setattr__. Only the class that *defines*
        # value is wrapped; subclasses inherit the cached descriptor.
        prop = cls.__dict__.get("value")
        if isinstance(prop, property) and prop.fget is not None:
            cached = cached_property(prop.fget)
            cached.__set_name__(cls, "value")
            cls.value = cached  # type: ignore[assignment]

        # Wrap a custom __init__ so field types are checked after construction. The
        # type checker still reads the source __init__ signature for argument
        # checking; this only adds the runtime guard. (A dataclass-generated __init__
        # isn't present yet at __init_subclass__ time and is not wrapped.)
        user_init = cls.__dict__.get("__init__")
        if callable(user_init):

            @wraps(user_init)
            def checked_init(
                self: Header,
                *args: object,
                _init: Callable[..., object] = user_init,
                **kwargs: object,
            ) -> None:
                _init(self, *args, **kwargs)
                self._check_field_types()

            cls.__init__ = checked_init  # type: ignore[assignment]

    @property
    @abstractmethod
    def value(self) -> str:
        """The serialized header field value (without the name)."""

    def __str__(self) -> str:
        """Return the full ``Name: value`` header field."""
        return f"{self.name}: {self.value}"

    def __bytes__(self) -> bytes:
        return str(self).encode(self.encoding)

    @property
    def asgi_value(self) -> tuple[bytes, bytes]:
        """Return a ``(name, value)`` pair of latin-1 bytes for an ASGI send dict.

        ASGI encodes header values as ISO-8859-1 (latin-1); using the class
        encoding keeps this consistent with ``__bytes__`` and accepts obs-text.
        """
        return (self.name.encode(self.encoding), self.value.encode(self.encoding))

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Header) and type(other) is type(self):
            return (self.name, self.value) == (other.name, other.value)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.name, self.value))

    @classmethod
    def _field_hints(cls) -> dict[str, object]:
        """Resolved ``{field_name: type_hint}`` for this header's dataclass fields,
        cached per class. Annotations are resolved per class across the MRO (so an
        unresolvable annotation on one class doesn't disable the check for others)."""
        cached = cls.__dict__.get("_field_hints_cache")
        if cached is None:
            merged: dict[str, Any] = {}
            for klass in reversed(cls.__mro__):  # base -> derived; derived wins
                try:
                    merged.update(inspect.get_annotations(klass, eval_str=True))
                except Exception:
                    continue
            cached = {
                f.name: merged[f.name]
                for f in dataclasses.fields(cls)  # type: ignore[arg-type]
                if f.name in merged
            }
            cls._field_hints_cache = cached
        return cached

    def __post_init__(self) -> None:
        # Field-type check for headers with a dataclass-generated __init__ (which
        # calls __post_init__). Custom __init__s are wrapped in __init_subclass__
        # instead. A subclass overriding __post_init__ should call super() to keep
        # this guard (or it must validate its fields another way).
        self._check_field_types()

    def _check_field_types(self) -> None:
        """Runtime enforcement of the construction contract: every field must match
        its declared type. Because each field type validates itself on creation, a
        type check is a complete guarantee -- no grammar re-parse. Raises TypeError
        (pointing to :meth:`parse`) on a mismatch."""
        for name, hint in type(self)._field_hints().items():
            value = getattr(self, name)
            if not _matches_type(value, hint):
                cls_name = type(self).__name__
                shown = repr(value)
                if len(shown) > 60:
                    shown = shown[:57] + "..."
                raise TypeError(
                    f"{cls_name}.{name} expects {hint!r}; got {shown}. Use "
                    f"{cls_name}.parse() to build a {cls_name} from a string."
                )

    @classmethod
    def _check_length(cls, value: str) -> None:
        """Reject an oversized parse() input before the (super-linear) grammar runs."""
        if len(value) > cls.max_length:
            raise ValueError(
                f"{cls.__name__} value of {len(value)} chars exceeds the maximum "
                f"of {cls.max_length}."
            )

    @classmethod
    def _node(cls, value: str) -> Node:
        """Parse ``value`` against ``cls.rule``, translating a ParseError to a ValueError."""
        cls._check_length(value)
        try:
            return cls.rule.parse_all(value)
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    @classmethod
    def _prefixed_node(cls, value: str) -> Node:
        """Like :meth:`_node`, but for grammar rules that match the whole header line (name
        included); prepend ``"<name>: "`` before parsing."""
        cls._check_length(value)
        try:
            return cls.rule.parse_all(f"{cls.name}: {value}")
        except ParseError as exc:
            raise ValueError(f'Invalid {cls.__name__} value "{value}".') from exc

    @classmethod
    def parse(cls, value: str) -> Header:
        """Parse a header value into an instance. Every concrete known header overrides this
        (CustomHeader carries an arbitrary name and is built via its constructor instead)."""
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, value: str) -> Header:
        """Return a header for ``(name, value)``: a matching known subclass if one is
        registered for ``name``, otherwise a :class:`CustomHeader`."""
        lname = name.lower()
        for subcls in cls.subclass_tree():
            cls_name = getattr(subcls, "name", None)
            if isinstance(cls_name, str) and cls_name.lower() == lname:
                return subcls.parse(value)
        return CustomHeader(name, value)

    @classmethod
    def subclass_tree(cls) -> Iterable[type[Header]]:
        """Yield all Header subclasses, depth-first."""
        for subcls in cls.__subclasses__():
            yield subcls
            yield from subcls.subclass_tree()


@dataclass(frozen=True)
class CustomHeader(Header):
    """A header with an arbitrary field name, e.g. ``X-Request-Id``.

    Both name and value are validated against RFC 9110 (``field-name`` / ``field-value``).
    """

    rule: ClassVar[Rule] = rfc9110.Rule("field-value")

    field_name: FieldName
    field_value: FieldValue

    def __init__(self, name: str, value: str) -> None:
        object.__setattr__(self, "field_name", FieldName(name))
        object.__setattr__(self, "field_value", FieldValue(value))

    @property
    def name(self) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self.field_name

    @property
    def value(self) -> str:
        return self.field_value

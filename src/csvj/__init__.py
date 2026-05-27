"""Reader and writer for CSVJ files (https://csvj.org).

The public surface is two functions:

- :func:`parse` — parse CSVJ bytes/text into a :class:`Table`.
- :func:`stringify` — serialize a :class:`Table` back to CSVJ text.

Both are placeholders until the reader/writer implementation lands
(PLAN §7c.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

__all__ = [
    "Table",
    "Value",
    "ParseError",
    "WriteError",
    "parse",
    "stringify",
]

Value = Union[str, int, float, bool, None]
"""A CSVJ value. CSVJ inherits JSON's value model restricted to scalars:
strings, numbers, booleans, and ``None`` (no nested arrays or objects)."""


@dataclass
class Table:
    """A parsed CSVJ table: a header row plus zero or more data rows.

    ``header`` is a list of column names (strings, zero or more, all
    distinct). ``rows`` is a list of rows; each row has exactly
    ``len(header)`` :data:`Value` entries.
    """

    header: list[str] = field(default_factory=list)
    rows: list[list[Value]] = field(default_factory=list)


class ParseError(ValueError):
    """Raised by :func:`parse` when the input is not valid CSVJ."""


class WriteError(ValueError):
    """Raised by :func:`stringify` when the table cannot be serialized."""


def parse(_input: str | bytes) -> Table:
    """Parse CSVJ input into a :class:`Table`.

    Not yet implemented — raises :class:`ParseError` with a
    "not yet implemented" message. The signature is stable.
    """

    raise ParseError("csvj.parse is not yet implemented")


def stringify(_table: Table) -> str:
    """Serialize a :class:`Table` back to CSVJ text.

    Not yet implemented — raises :class:`WriteError` with a
    "not yet implemented" message. The signature is stable.
    """

    raise WriteError("csvj.stringify is not yet implemented")

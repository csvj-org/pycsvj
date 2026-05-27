"""Reader and writer for CSVJ files (https://csvj.org).

The public surface is two functions:

- :func:`parse` — parse CSVJ text into a :class:`Table`.
- :func:`stringify` — serialize a :class:`Table` back to CSVJ text.

Strict §1 from day one: empty input, missing trailing newline, ragged
rows, and duplicate header names are rejected. Values are restricted to
``str | int | float | bool | None`` — anything else (arrays, objects,
NaN, Infinity) is rejected on parse and on stringify.
"""

from __future__ import annotations

import json
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


def parse(input: str | bytes) -> Table:
    """Parse CSVJ input into a :class:`Table`.

    Accepts either :class:`str` or :class:`bytes`; bytes are decoded as
    UTF-8. Raises :class:`ParseError` on any input the spec says must
    be rejected.
    """

    if isinstance(input, bytes):
        try:
            text = input.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ParseError(f"input is not valid UTF-8: {e}") from None
    else:
        text = input

    if text == "":
        raise ParseError("empty input")
    if not text.endswith("\n"):
        raise ParseError("file does not end with newline")

    body = text[:-1]
    raw_lines = body.split("\n")

    lines = []
    for line in raw_lines:
        if line.endswith("\r"):
            line = line[:-1]
        lines.append(line)

    header_values = _parse_line(lines[0], "header")
    header: list[str] = []
    for v in header_values:
        if not isinstance(v, str):
            raise ParseError("non-string item at csvj header")
        header.append(v)

    seen: dict[str, bool] = {}
    for name in header:
        if name in seen:
            raise ParseError(f"duplicate header name {json.dumps(name)}")
        seen[name] = True

    rows: list[list[Value]] = []
    header_len = len(header)
    for idx, line in enumerate(lines[1:], start=1):
        row = _parse_line(line, f"row {idx}")
        if len(row) != header_len:
            raise ParseError(
                f"row {idx} has {len(row)} values, header has {header_len}"
            )
        rows.append(row)

    return Table(header=header, rows=rows)


def stringify(table: Table) -> str:
    """Serialize a :class:`Table` back to CSVJ text.

    Output is terminated by ``\\n``. Every row must have exactly
    ``len(table.header)`` values, and each value must be ``str``,
    ``int``, ``float``, ``bool``, or ``None``. Non-finite floats
    (NaN / ±Infinity) are rejected. Raises :class:`WriteError` on any
    other input.
    """

    if not isinstance(table, Table):
        raise WriteError("argument must be a csvj.Table")

    header = table.header
    for i, v in enumerate(header):
        if not isinstance(v, str):
            raise WriteError(f"header item {i} is not a string")

    seen: dict[str, bool] = {}
    for name in header:
        if name in seen:
            raise WriteError(f"duplicate header name {json.dumps(name)}")
        seen[name] = True

    header_len = len(header)
    out = [_serialize_row(header)]

    for i, row in enumerate(table.rows):
        if not isinstance(row, list):
            raise WriteError(f"row {i} is not a list")
        if len(row) != header_len:
            raise WriteError(
                f"row {i} has {len(row)} values, expected {header_len}"
            )
        out.append(_serialize_row(row))

    return "\n".join(out) + "\n"


def _forbid_constant(name: str) -> None:
    raise ValueError(f"forbidden constant {name!r}")


def _parse_line(body: str, label: str) -> list[Value]:
    try:
        decoded = json.loads("[" + body + "]", parse_constant=_forbid_constant)
    except ValueError as e:
        raise ParseError(f"{label} parse error: {e}") from None

    if not isinstance(decoded, list):
        raise ParseError(f"{label} parse error: not a JSON array")

    for i, v in enumerate(decoded):
        if v is None or isinstance(v, str):
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            continue
        raise ParseError(f"{label} parse error at item {i}")

    return decoded


def _serialize_row(row: list[Value]) -> str:
    for i, v in enumerate(row):
        if v is None or isinstance(v, (str, bool)):
            continue
        if isinstance(v, int):
            continue
        if isinstance(v, float):
            if v != v or v in (float("inf"), float("-inf")):
                raise WriteError(
                    f"item {i} is not CSVJ type-safe: non-finite number"
                )
            continue
        raise WriteError(
            f"item {i} is not CSVJ type-safe: {type(v).__name__}"
        )

    json_text = json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    return json_text[1:-1]

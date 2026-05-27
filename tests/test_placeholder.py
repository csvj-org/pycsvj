"""Smoke tests for the placeholder public surface.

These exist so CI exercises something on day one. They will be replaced
by the real reader/writer tests in PLAN §7c.2.
"""

from __future__ import annotations

import pytest

import csvj


def test_parse_is_placeholder() -> None:
    with pytest.raises(csvj.ParseError, match="not yet implemented"):
        csvj.parse("\n")


def test_stringify_is_placeholder() -> None:
    with pytest.raises(csvj.WriteError, match="not yet implemented"):
        csvj.stringify(csvj.Table())


def test_table_default_is_empty() -> None:
    table = csvj.Table()
    assert table.header == []
    assert table.rows == []


def test_parse_error_is_value_error() -> None:
    assert issubclass(csvj.ParseError, ValueError)


def test_write_error_is_value_error() -> None:
    assert issubclass(csvj.WriteError, ValueError)

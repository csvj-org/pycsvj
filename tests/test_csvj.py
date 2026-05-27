"""Unit tests for csvj.parse and csvj.stringify.

Ported from csvj-org/phpcsvj's CsvjTest.php so the two reference
implementations agree on the same behavioral surface.
"""

from __future__ import annotations

import math

import pytest

import csvj


def test_parse_simple_strings() -> None:
    table = csvj.parse(
        '"Header1", "Header2", "Header3"\n'
        '"Row1", "Row2", "Row3"\n'
    )
    assert table.header == ["Header1", "Header2", "Header3"]
    assert table.rows == [["Row1", "Row2", "Row3"]]


def test_parse_mixed_types() -> None:
    table = csvj.parse(
        '"h1", "h2", "h3"\n'
        '42, 3.14, false\n'
        'null, true, "trailing"\n'
    )
    assert table.header == ["h1", "h2", "h3"]
    assert table.rows == [
        [42, 3.14, False],
        [None, True, "trailing"],
    ]


def test_parse_crlf_line_endings() -> None:
    table = csvj.parse('"h1","h2","h3"\r\n1,2,3\r\n')
    assert table.header == ["h1", "h2", "h3"]
    assert table.rows == [[1, 2, 3]]


def test_parse_utf8_values() -> None:
    table = csvj.parse(
        '"h1", "h2", "h3"\n'
        '"héllo", "日本語", "🚀"\n'
    )
    assert table.rows == [["héllo", "日本語", "🚀"]]


def test_parse_json_escapes() -> None:
    table = csvj.parse(
        '"h1", "h2", "h3", "h4"\n'
        '"line1\\nline2", "tab\\there", "quote\\"end", "backslash\\\\"\n'
    )
    assert table.rows == [["line1\nline2", "tab\there", 'quote"end', "backslash\\"]]


def test_parse_unicode_escape_surrogate_pair() -> None:
    table = csvj.parse('"h1", "h2"\n"\\u00e9", "\\uD83D\\uDE00"\n')
    assert table.rows == [["é", "😀"]]


def test_parse_number_forms() -> None:
    table = csvj.parse(
        '"a", "b", "c", "d", "e"\n'
        '-1, 0, 1.5, 1e10, -2.5e-3\n'
    )
    row = table.rows[0]
    assert row[0] == -1 and isinstance(row[0], int)
    assert row[1] == 0 and isinstance(row[1], int)
    assert row[2] == 1.5 and isinstance(row[2], float)
    assert row[3] == 1e10
    assert math.isclose(row[4], -2.5e-3)


def test_parse_booleans_and_null() -> None:
    table = csvj.parse('"h1", "h2", "h3", "h4"\ntrue, false, null, "string"\n')
    assert table.rows == [[True, False, None, "string"]]


def test_parse_multiple_rows() -> None:
    table = csvj.parse('"h1", "h2"\n1, 2\n3, 4\n5, 6\n')
    assert table.rows == [[1, 2], [3, 4], [5, 6]]


def test_parse_long_value() -> None:
    long = "a" * 4096
    table = csvj.parse(f'"h1"\n"{long}"\n')
    assert table.rows[0][0] == long


def test_parse_trailing_null_and_empty_string() -> None:
    table = csvj.parse(
        '"a", "b", "c"\n'
        '"x", "y", null\n'
        '"p", "q", ""\n'
    )
    assert table.rows == [["x", "y", None], ["p", "q", ""]]


def test_parse_empty_header_line() -> None:
    table = csvj.parse("\n")
    assert table.header == []
    assert table.rows == []


def test_parse_empty_header_line_crlf() -> None:
    table = csvj.parse("\r\n")
    assert table.header == []
    assert table.rows == []


def test_parse_accepts_bytes() -> None:
    table = csvj.parse(b'"h1"\n"x"\n')
    assert table.header == ["h1"]
    assert table.rows == [["x"]]


def test_parse_rejects_invalid_utf8_bytes() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse(b"\xff\xfe\n")


def test_reject_empty_file() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse("")


def test_reject_missing_trailing_newline() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"h1", "h2"')


def test_reject_missing_trailing_newline_after_data_row() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"h1"\n42')


def test_reject_ragged_short_row() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n"x", "y"\n')


def test_reject_ragged_long_row() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b"\n"x", "y", "z"\n')


def test_reject_empty_line_in_middle() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"h1", "h2"\n\nnull, true\n')


def test_reject_duplicate_header_names() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "a"\n')


def test_reject_duplicate_empty_headers() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"", ""\n')


def test_reject_non_string_header() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", 42, "b"\n')


def test_reject_array_value() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n1, [], 3\n')


def test_reject_object_value() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n1, {}, 3\n')


def test_reject_bare_token() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n1, $, 3\n')


def test_reject_leading_zeros() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a"\n0123\n')


def test_reject_nan() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, NaN, false\n')


def test_reject_infinity() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, Infinity, false\n')


def test_reject_negative_infinity() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, -Infinity, false\n')


def test_reject_uppercase_true() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, True, false\n')


def test_reject_uppercase_null() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, Null, false\n')


def test_reject_single_quoted_string() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, \'hi\', false\n')


def test_reject_bare_dot_number() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, .5, false\n')


def test_reject_trailing_dot_number() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, 1., false\n')


def test_reject_unescaped_control_char() -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse('"a", "b", "c"\n42, "hello\x01world", false\n')


def test_stringify_simple() -> None:
    out = csvj.stringify(csvj.Table(header=["h1", "h2"], rows=[[1, 2], [3, 4]]))
    assert out == '"h1","h2"\n1,2\n3,4\n'


def test_stringify_mixed_types() -> None:
    out = csvj.stringify(
        csvj.Table(
            header=["a", "b", "c", "d"],
            rows=[["x", 1, True, None], ["y", 2.5, False, ""]],
        )
    )
    assert out == '"a","b","c","d"\n"x",1,true,null\n"y",2.5,false,""\n'


def test_stringify_empty_header_line() -> None:
    assert csvj.stringify(csvj.Table()) == "\n"


def test_stringify_escapes_special_chars() -> None:
    out = csvj.stringify(
        csvj.Table(header=["h1"], rows=[["line\nbreak"], ['quote"end']])
    )
    assert out == '"h1"\n"line\\nbreak"\n"quote\\"end"\n'


def test_stringify_preserves_utf8() -> None:
    out = csvj.stringify(csvj.Table(header=["h1"], rows=[["日本語"]]))
    assert out == '"h1"\n"日本語"\n'


def test_stringify_rejects_duplicate_header() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a", "a"]))


def test_stringify_rejects_non_string_header() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a", 42]))  # type: ignore[list-item]


def test_stringify_rejects_row_length_mismatch() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a", "b"], rows=[[1]]))


def test_stringify_rejects_nan() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a"], rows=[[float("nan")]]))


def test_stringify_rejects_infinity() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a"], rows=[[float("inf")]]))


def test_stringify_rejects_object_value() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a"], rows=[[{"k": 1}]]))  # type: ignore[list-item]


def test_stringify_rejects_array_value() -> None:
    with pytest.raises(csvj.WriteError):
        csvj.stringify(csvj.Table(header=["a"], rows=[[[1, 2]]]))  # type: ignore[list-item]


def test_round_trip() -> None:
    table = csvj.Table(
        header=["name", "age", "active"],
        rows=[
            ["alice", 30, True],
            ["bob", 25, False],
            ["carol", None, True],
        ],
    )
    out = csvj.stringify(table)
    parsed = csvj.parse(out)
    assert parsed == table

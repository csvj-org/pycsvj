# pycsvj

[![CI](https://github.com/csvj-org/pycsvj/actions/workflows/ci.yml/badge.svg)](https://github.com/csvj-org/pycsvj/actions/workflows/ci.yml)

Python reader and writer for [CSVJ](https://csvj.org) files. Python 3.10+.

## Overview

CSVJ is a tabular data format where each value is a JSON literal. The
spec is at <https://csvj.org>; the Go reference implementation lives at
[csvj-org/gocsvj](https://github.com/csvj-org/gocsvj), the JavaScript
reference at [csvj-org/jscsvj](https://github.com/csvj-org/jscsvj), the
PHP reference at [csvj-org/phpcsvj](https://github.com/csvj-org/phpcsvj),
the Rust reference at [csvj-org/rscsvj](https://github.com/csvj-org/rscsvj),
and the language-agnostic conformance suite at
[csvj-org/conformance](https://github.com/csvj-org/conformance).

The reader will enforce every §1 rule (empty input rejected; trailing
newline required; ragged rows rejected; duplicate header names
rejected; only `str | int | float | bool | None` permitted at value
position; JSON lexical rules per RFC 8259) and pass all 25 vectors of
`csvj-org/conformance@master`.

## Parse

```python
import csvj

table = csvj.parse('"name","age"\n"alice",30\n"bob",null\n')
# table.header == ["name", "age"]
# table.rows == [
#     ["alice", 30],
#     ["bob", None],
# ]
```

The returned `Table` has a `header` field (`list[str]`, zero or more
column names) and a `rows` field (`list[list[Value]]`) where every row
has exactly `len(table.header)` values. Each value is `str`, `int`,
`float`, `bool`, or `None`.

Parsing rejects every input the spec says must be rejected — see the
[conformance suite](https://github.com/csvj-org/conformance) for the
full list. Invalid input raises `csvj.ParseError`.

## Serialize

```python
import csvj

bytes_out = csvj.stringify(csvj.Table(
    header=["name", "age"],
    rows=[
        ["alice", 30],
        ["bob", None],
    ],
))
# bytes_out == '"name","age"\n"alice",30\n"bob",null\n'
```

The output is always spec-compliant CSVJ: terminated by `\n`, every row
has exactly `len(table.header)` values, and every value is encoded as a
JSON literal.

## Status

`parse` and `stringify` are currently placeholders that raise
`csvj.ParseError` / `csvj.WriteError` with a "not yet implemented"
message. The public surface (`Table`, `Value`, `ParseError`,
`WriteError`, `parse`, `stringify`) is stable so consumers can pin
against it before the reader/writer lands (PLAN §7c.2).

## Install

```sh
pip install pycsvj
```

(Not yet published to PyPI — see
[PLAN.md §6d](https://github.com/csvj-org/website) for the publication
checklist.)

## License

MIT — see [LICENSE](LICENSE).

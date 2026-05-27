"""Drives the language-agnostic conformance suite from
https://github.com/csvj-org/conformance against this checkout.

Vector tree root is taken from the ``CSVJ_CONFORMANCE_DIR`` env var,
set by the ``conformance`` GHA job. The whole module is skipped when
the env var is unset so that default local ``pytest`` runs do not
require a sibling conformance checkout.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import csvj

_CONFORMANCE_DIR = os.environ.get("CSVJ_CONFORMANCE_DIR")
if not _CONFORMANCE_DIR:
    pytest.skip(
        "CSVJ_CONFORMANCE_DIR not set — point it at a checkout of "
        "csvj-org/conformance to run this suite",
        allow_module_level=True,
    )

_VECTOR_ROOT = Path(_CONFORMANCE_DIR)


def _accept_vectors() -> list[pytest.param]:
    inputs = sorted((_VECTOR_ROOT / "inputs").glob("*.csvj"))
    if not inputs:
        raise RuntimeError(f"no inputs/*.csvj vectors found under {_VECTOR_ROOT}")
    return [pytest.param(p, _VECTOR_ROOT / "expected" / f"{p.stem}.json", id=p.stem) for p in inputs]


def _reject_vectors() -> list[pytest.param]:
    rejects = sorted((_VECTOR_ROOT / "must-reject").glob("*.csvj"))
    if not rejects:
        raise RuntimeError(f"no must-reject/*.csvj vectors found under {_VECTOR_ROOT}")
    return [pytest.param(p, id=p.stem) for p in rejects]


@pytest.mark.parametrize(("input_path", "expected_path"), _accept_vectors())
def test_accept_vector(input_path: Path, expected_path: Path) -> None:
    table = csvj.parse(input_path.read_bytes())
    got = [table.header, *table.rows]
    want = json.loads(expected_path.read_text())
    assert got == want, f"vector {input_path}"


@pytest.mark.parametrize("input_path", _reject_vectors())
def test_reject_vector(input_path: Path) -> None:
    with pytest.raises(csvj.ParseError):
        csvj.parse(input_path.read_bytes())

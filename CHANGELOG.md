# Changelog

All notable changes to this project will be documented in this file. The
format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not follow Semantic Versioning until 1.0.0; before
then breaking changes may occur in any release.

## [Unreleased]

### Added

- Initial repository scaffolding: hatchling-built distribution `pycsvj`
  (import name `csvj`), pytest, GHA CI matrix over Python 3.10 / 3.11 /
  3.12 / 3.13 with SHA-pinned third-party actions, Dependabot config
  for pip and github-actions, MIT license, three-section README.
- `csvj.parse` reader and `csvj.stringify` writer with strict §1
  enforcement: empty input rejected, trailing newline required, ragged
  rows rejected, duplicate header names rejected, values restricted to
  `str | int | float | bool | None` (with non-finite floats rejected on
  both parse and stringify, and `NaN` / `Infinity` rejected as parse
  tokens via the json `parse_constant` hook). 50-case pytest suite plus
  local verification against all 25 vectors of
  [csvj-org/conformance@master](https://github.com/csvj-org/conformance).
- CI job that runs the `csvj-org/conformance@master` suite on every
  push and PR: checks out conformance alongside pycsvj and runs
  `pytest tests/conformance` with `CSVJ_CONFORMANCE_DIR` set. Local
  `pytest` runs skip the conformance suite when the env var is unset.

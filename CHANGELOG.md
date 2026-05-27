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
- `csvj.parse` and `csvj.stringify` are placeholders that raise
  `csvj.ParseError` / `csvj.WriteError` with a "not yet implemented"
  message so consumers can pin against the public surface (`Table`,
  `Value`, `ParseError`, `WriteError`, `parse`, `stringify`) before the
  reader/writer lands.

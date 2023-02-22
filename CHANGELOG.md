# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

```
## [_._._] - 20XX-MM-DD

### Added
-
### Changed
-
### Removed
-
```

## [0.6.0] - 2023-02-22
### Added
- structure containing modex example in tests

### Changed
- default parent directory for collections and structures dirs to current working dir

## [0.5.0] - 2023-02-15

### Added
- mypy linting
- models for ES structure

### Changed
- process dateframes are merged and returned as scalars and timeseries
- regions are unpacked and merged in process dataframes
- versioned collection metadata

## [0.4.1] - 2023-01-23

### Fixed
- reading of annotation


## [0.4.0]

### Added
- checks for annotations of collection

### Changed
- collection metadata holds data type (Note: Collections have to be reloaded)
- data import via frictionless (converts timeseries to list-of-floats while loading)

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

## [0.14.0] - 2023-12-01
### Added
- collection function to get artifact by name

## [0.13.2] - 2023-12-01
### Fixed
- removed legacy sqlalchemy engine

## [0.13.1] - 2023-11-08
### Fixed
- latest version for versions > v9

## [0.13.0] - 2023-11-07
### Fixed
- databus endpoint, SPARQLing and related tests

## [0.12.0] - 2023-11-02
### Changed
- foreign keys are given in datasets instead of links

## [0.11.2] - 2023-08-17
### Fixed
- timeseries refactoring for multiple periods

## [0.11.1] - 2023-08-17
### Fixed
- typing error for python versions <3.10

## [0.11.0] - 2023-07-25
### Changed
- timeseries are turned into dataframes with timeindex and multiindex columns containing name and regions

## [0.10.0] - 2023-04-26
### Added
- allow multiple (sub-)processes per table

### Changed
- collection metadata can contain multiple names and subjects per artifact

## [0.9.1] - 2023-04-21
### Fixed
- links in `get_process` function

## [0.9.0] - 2023-03-31
### Changed
- introduced Adapter class to handle collection, structure and links in a centralized way

## [0.8.0] - 2023-02-27
### Changed
- by default, process and parameter names are not derived from annotations, but from name in metadata and column names

## [0.7.0] - 2023-02-27
### Changed
- "additional parameters" are renamed to "links" and are read-in from CSV

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

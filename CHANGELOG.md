# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add require option to tower.get

## [1.5.2] - 2021-02-10
### Fixed
- Compatibility issues with Salt 2017

## [1.5.1] - 2021-02-10
### Fixed
- Missing symlink to new filter renderer from `_renderers` directory for gitfs deployments

## [1.5.0] - 2021-02-10
### Added
- `filter` renderer returning only a matching subset from a dataset (e.g. YAML)

## [1.4.0] - 2021-01-29
### Added
- Support for Python 3.8 and 3.9, and Salt 3001 and 3002

## [1.3.1] - 2020-05-11
### Fixed
- Fix mutation of context variables when rendering multiple files

## [1.3.0] - 2020-05-11
### Added
- Added `merge-last`, `merge-first`, `remove` and `overwrite` merge strategies for dictionaries
- Improve logging source and exception for rendering errors (#10)
- Extended `render` context function to support relative lookup

### Fixed
- Fix `render` context function to use correct `basedir` variable
- Add `basedir` variable when rendering top file

## [1.2.0] - 2020-01-31
### Added
- Provide `basedir` context variable for absolute includes, e.g. `!include {{ basedir }}/files/config.ini`
- Support loading pillar and renderer modules via gitfs and sync runner

## [1.1.0] - 2019-03-10
### Added
- Pillar include supports relative includes using only `./` and `../`
- Compatible with new salt 2019.2

## 1.0.0 - 2018-11-16
### Added
- First version of ext pillar
  - First version of ext pillar
  - Yamlet and Text renderer

[Unreleased]: https://github.com/jgraichen/salt-tower/compare/v1.5.2...HEAD
[1.5.2]: https://github.com/jgraichen/salt-tower/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/jgraichen/salt-tower/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/jgraichen/salt-tower/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/jgraichen/salt-tower/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/jgraichen/salt-tower/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/jgraichen/salt-tower/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/jgraichen/salt-tower/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jgraichen/salt-tower/compare/v1.0.0...v1.1.0

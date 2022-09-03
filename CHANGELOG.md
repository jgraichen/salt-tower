# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add `key` argument to filter renderer returning result in a nested dictionary

## [1.9.0] - 2022-05-16

### Added

- Enabling `salt_tower.raise_on_missing_files` will raise an error when an included file does not exist
- Include in `tower.sls` can be marked as optional

## [1.8.2] - 2021-12-03

### Fixed

- Trying to release a versioned documentation

## [1.8.1] - 2021-12-03

### Fixed

- Trying to release a versioned documentation

## [1.8.0] - 2021-12-03

### Added

- [Alternative directory include mode](https://jgraichen.github.io/salt-tower/v1.8.2/configuration/#include_directory_mode)

## [1.7.0] - 2021-04-03

### Fixed

- Python package loader for Salt 3003
- Calling conventions to have more salt renderer lookup files relative to current template (e.g. JINJA `include`) (#11)

### Added

- Tower compatibility with Salt 3003 (#18)
- Experimental flag to have some renderers (e.g. JINJA) lookup files in `pillar_roots` (#11)

## [1.6.0] - 2021-03-09

### Added

- Add require option to `tower.get`
- Experimental: Support custom context in template injected `render` function
- Deep scrubbing of merge strategies (`__`) from merged pillar data

## [1.5.2] - 2021-02-10

### Fixed

- Compatibility issues with Salt 2017

## [1.5.1] - 2021-02-10

### Fixed

- Missing symlink to new filter renderer from `_renderers` directory for `gitfs` deployments

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
- Support loading pillar and renderer modules via `gitfs` and sync runner

## [1.1.0] - 2019-03-10

### Added

- Pillar include supports relative includes using only `./` and `../`
- Compatible with new salt 2019.2

## 1.0.0 - 2018-11-16

### Added

- First version of ext pillar
  - First version of ext pillar
  - Yamlet and Text renderer

[unreleased]: https://github.com/jgraichen/salt-tower/compare/v1.9.0...HEAD
[1.9.0]: https://github.com/jgraichen/salt-tower/compare/v1.8.2...v1.9.0
[1.8.2]: https://github.com/jgraichen/salt-tower/compare/v1.8.1...v1.8.2
[1.8.1]: https://github.com/jgraichen/salt-tower/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/jgraichen/salt-tower/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/jgraichen/salt-tower/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/jgraichen/salt-tower/compare/v1.5.2...v1.6.0
[1.5.2]: https://github.com/jgraichen/salt-tower/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/jgraichen/salt-tower/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/jgraichen/salt-tower/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/jgraichen/salt-tower/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/jgraichen/salt-tower/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/jgraichen/salt-tower/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/jgraichen/salt-tower/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jgraichen/salt-tower/compare/v1.0.0...v1.1.0

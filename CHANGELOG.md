# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) from version [3.0.0] on.
This Project entered open source status with version 2.1.0.
Older versions are not not part of this Project.

## [Unreleased]

## [3.2.0] - 2019-05-29

## Added

- Management commands to work with the elasticsearch index

### Changed

- Reword Documentation and LICENSE.md file to let GitHub recognize the Project as AGPL-3.0.
- Combined staging and production settings.
- Improved admin interface.
- Improved admin model functionality.
- Update models of data app.
- Update models of instruments app.

## [3.1.0] - 2019-05-23

### Added

- This Changelog.
- Many redundant commits due to unresolveable merge conflicts.
- Automatic update of stale static files kept in the static_data volume.
- Section to README to explain the currently hackey way the elastic search index is configured.

### Changed

- Storage location for data to be imported can now be set via environment variable.
- Update dependencies.

### Fixed

- Pavement command to create elasticsearch index.

### Removed

- Unused codecov library from Pipfile.

## [3.0.1] - 2019-05-20

### Added

- Install section for Production to README.

### Changed

- Update Readme.
- Update Dependencies.
- Refactor dependency files.

### Fixed

- Sending of coverage data to codecov.io

### Removed

- Fabric from dependencies

## [3.0.0] - 2019-05-17

### Added

- docker setup.
- docker-compose setup.
- docker-compose development setup.
- Example config and `ENVIRONMENT` files for the use with the docker setup.
- Some configuration can now be set via environment variables.
- Use of PostgreSQL database.
- Use of dedicated mail server service.
- Adherence to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for this project.

### Changed

- Data Model: Question labels type from CharField to TextField.
- Travis setup to work with docker.
- Tests to work with docker;
- Installation Section in Readme to explain docker setup.
- Elasticsearch version to 2.4.6.

### Deprecated

- Installation of project without docker
- Use of paver to set up project is phased out in future versions

### Removed

- Import: Data is no longer pulled via `--depth 1`.

## [2.1.0] 2018-12-05

### Changed

- Moved Project into Open Source and onto GitHub.:rocket:
- Codestyle to work with flake8

[Unreleased]: https://github.com/ddionrails/ddionrails/compare/v3.1.1...HEAD
[3.1.1]: https://github.com/ddionrails/ddionrails/compare/v3.1.0...v3.1.1
[3.1.0]: https://github.com/ddionrails/ddionrails/compare/v3.0.1...v3.1.0
[3.0.1]: https://github.com/ddionrails/ddionrails/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/ddionrails/ddionrails/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/ddionrails/ddionrails/releases/tag/v2.1.0
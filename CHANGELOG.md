# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html)
from version [3.0.0] on.
This Project entered open source status with version 2.1.0.
Older versions are not not part of this Project.

## [Unreleased]

## [4.1.0] - 2019-08-28

### Added

- A Warning is now displayed for Internet Explorer users.

  - IE is not supported and the warning suggests the use of a different Browser.

- dev: pre-push hook can be installed to spellcheck commit messages.

### Changed

- dev: All pre-commit hooks are now local.
- Switched source for `django-elasticsearch-dsl` from GitHub to PyPi.
- Python packages are now installed via `pip` instead of `pipenv install --system`.
- Update `README.md` to reflect changes in the Docker setup.

### Fixed

- dev: removed leftover volume definition from remote-dev docker-compose file.

## [4.0.2] - 2019-08-22

### Added

- Favicon and webpack setup.

### Changed

- Raised rqworker default Timeout.
- Refactored Vue router.
- Revised update section in home.html template.
- Update dependencies.

### Fixed

- Creation of answer tables on question views works again.
- Facet checkbox does no longer shrink when facet text gets to long.
- Hyperrefs at the end of the CHANGELOG.md.
- Responsive mobile menu now collapses correctly.

## [4.0.1] - 2019-08-16

### Fixed

- Adjust variable_detail.html django template to Bootstrap 4.
- Further separated dev and production setup to keep content of static/dist in production.

  - Dockerfile and dev.Dockerfile use different entrypoint.sh.
  - Dockerfile entrypoint no longer contains rebuilding section for npm packages.

## [4.0.0] - 2019-08-13

### Added<a id="4.0.0_added"></a>

- container health checks.
- CONTRIBUTING.md.
- Different image setups for development and live systems.
- doi field to Study.
- label_de field to ddionrails.instruments.Instrument.

### Changed

- Database and search engine import were decoupled.

  - Search engine import is done via management command `search_index --populate`.
  - When calling the `update` management command, `search_index --populate`
    is called implicitly after imports are finished.

- Development setup is now focused on remote 'in container' development.

- Django management commands `update` and `upgrade` were merged.

  - Now `update` loads remote data and starts the import.

- Downgrade compose version to 2.4.

  - Version 3 is geared towards use with swarm setups and provides many
    features only for use in a docker swarm.

- Elasticsearch is now proxied through Nginx instead of Django.
- :rocket: most models now use UUIDs as Primary Keys. [major change]

  - UUIDs are either generated from a base UUID and the content of the fields
    that make a row unique or from the UUID of the "parent" model and the  
    unique fields.

  - Numeric ids which were used until now are incompatible with the new UUID field.
    This breaking change was used as an opportunity to reset all migrations and
    start from a clean slate.

- :rocket: Replace ddionrails-elasticsearch with ReactiveSearch. [major change]
- Several dependency updates.
- Slimmed down [live](#4.0.0_added) docker image.
- Switched base image of postfix to vanilla alpine.
- Update Bootstrap to Bootstrap 4 and subsequent layout adaptations.
- Update Django version to 2.2.4.
- Update Elasticsearch to 7.3.0.
- Update Docker settings related to security.
- Use Python 3.7.4 as base for Django image.

### Fixed

- Gunicorn now correctly logs to docker.

### Removed

- "Magic at work!".
- Bootstrap 3.
- DatasetRedirectView.
- ddionrails-elasticsearch.
- Elasticsearch 2.
- lowercasing from ModelMixin.
- old migrations. New squashed ones now use UUIDs.
- several code smells identified by codacy.
- StudyRedirectView.
- workspace/angular.html template.

## [3.3.0] - 2019-06-18

### Added

- File server using django-filer.
- Setup for [renovate-bot](https://github.com/apps/renovate).
- pre-commit hooks for development.
- QuestionImage Model to store Images for Question Objects.
- Tests for paver tasks and api.view.

### Changed

- Restructure static file handling.

  - Moved static assets from static/src/ to assets/ directory.
  - Removed static folder from source tracking.
  - Update webpack.config.js.

- Update third party dependencies.
- Renamed media files folder from media_root to media.
- Move context from ddionrails.studies.models into own module.
- Move import_path() method from Study and System Models to new ImportPathMixin.
- Direct use of "/tmp/" replaced with use of tempfile library.
- imports.manager. Repository now uses GitPython.
- imports.manager. SystemImportManager now runs without django_rq.

### Removed

- Several unused templates and views.
- Unused or pre-installed packages from
  dockerfile package installation section.

- Security issues

  - use of preprocessing
  - use of os.system
  - use of eval

- Several outdated paver tasks.
- Forced storing of only lower cased names for Question and Variable names.

## [3.2.0] - 2019-05-29

### Added

- Management commands to work with the elasticsearch index

### Changed

- Reword Documentation and LICENSE.md file to let GitHub recognize the Project
  as AGPL-3.0.
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
- Section to README to explain the currently hackey way the elastic search index
  is configured.

### Changed

- Storage location for data to be imported can now be set via environment
  variable.

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
- Adherence to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for
  this project.

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

- Import: Data is no longer pulled via `--depth 1` .

## [2.1.0] 2018-12-05

### Changed

- Moved Project into Open Source and onto GitHub.:rocket:
- Codestyle to work with flake8

[unreleased]: https://github.com/ddionrails/ddionrails/compare/v4.1.0...develop
[4.1.0]: https://github.com/ddionrails/ddionrails/compare/v4.0.2...v4.1.0
[4.0.2]: https://github.com/ddionrails/ddionrails/compare/v4.0.1...v4.0.2
[4.0.1]: https://github.com/ddionrails/ddionrails/compare/v4.0.0...v4.0.1
[4.0.0]: https://github.com/ddionrails/ddionrails/compare/v3.3.0...v4.0.0
[3.3.0]: https://github.com/ddionrails/ddionrails/compare/v3.2.0...v3.3.0
[3.2.0]: https://github.com/ddionrails/ddionrails/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/ddionrails/ddionrails/compare/v3.0.1...v3.1.0
[3.0.1]: https://github.com/ddionrails/ddionrails/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/ddionrails/ddionrails/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/ddionrails/ddionrails/releases/tag/v2.1.0

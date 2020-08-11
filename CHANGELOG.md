# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html)
from version [3.0.0] on.
This Project entered open source status with version 2.1.0.
Older versions are not not part of this Project.

## [Unreleased]

## [4.6.1] - 2020-08-11

### Fixed

- A part of the concepts import still used only old field names.

## [4.6.0] - 2020-08-07

### Changed

- Import now works with data, as it was
  [specified](https://github.com/paneldata/data-specification).
- Made several imports able to fail by replacing catch all try, except blocks that
  let errors drop basically unhandled.
- Made several imports atomic.

## [4.5.4] - 2020-07-20

### Changed

- Bumped lodash dependency to 4.17.19 for important security update.

### Fixed

- 500 HTTP error that occurred with newer soep-core long datasets.

## [4.5.3] - 2020-07-14

### Fixed

- Import no longer fails, whe no concepts.csv is present.
- `Remove all` link in Basket view now works again.
- `Search in Study` navigational link now works on all pages it occurs.

## [4.5.2] - 2020-07-03

### Changed

- Downgrade reactivesearch-vue dependency to 1.2.0 since everything from 1.3.0
  breaks UI components.

- Reimplement clean-update to address data integrity issues.

  - A clean update now creates a backup of user basket data. Then the study data
    is deleted, reimported and the backup restored. The restored backup
    can introduce "dead" BasketVariables which are cleaned up at the end.

### Fixed

- Unittests that were not up to date.

## [4.5.1] - 2020-06-24

### Changed

- During production docker image build JavaScript and CSS libraries are now moved after
  building them with webpack.

  - They are moved back through the entrypoint script.
  - The shared static files volume for web and nginx container otherwise masks files
    in production setup.

- Migrate visualization.js from d3 <= v3 to >= v5.

  - d3 v4 brought in some breaking changes that had to be addressed.

- Recoupled Baskets with BasketVariables and BasketVariables with Variables due to
  data integrity problems.

### Fixed

- Corrected message displayed in base search UI, when no results are found.
- Instantiation of dataTable elements in UI.
- Question model called a non existent period attribute.

  - Period is now set for Questions during save.
  - Question Period == Instrument Period

## [4.5.0] - 2020-06-09

### Added

- "Search in Study" navigation link from a Study view.

  - User is directed to the search interface with the filter for the
    study already enabled.

### Changed

- Update ScriptGenerator in workspace

## [4.4.3] - 2020-05-26

### Added

- Flag to import without redis

### Fixed

- Abandoned Concepts (only found in variables.csv) are now handled explicitly.
- Concepts are now imported directly in the ConceptInput class not through an
  inherited function. The inherited function did no longer seem to work.

## [4.4.2] - 2020-05-04

### Changed

- Dangling BasketVariables are now removed after a full import of all variables
  instead of after all import jobs.

  - To guarantee that no basket variables are removed because of failed variable imports.
  - To no longer block the study update command since it is now part of a redis job.

- Removal of Dangling BasketVariables is now only performed for the study, that is
  currently imported to prevent accidental removal of variables when trying to update
  several studies.

### Fixed

- Authentication for the button to add variables to baskets now works in production.
- Added function to instantiate all dataTables on a page.

  - Display of dataTables had stopped working, probably through some dependency update.

## [4.4.1] - 2020-05-04

### Fixed

- Clean import no longer deletes baskets

## [4.4.0] - 2020-04-23

### Added

- `update` command flag -c --clean-import

  - Clean import deletes a study and all its associated data,
    except BasketVariables.
    The import then restores the study itself and continues
    importing from the studies metadata repository.

## [4.3.0] - 2020-04-21

### Added

- Several API endpoints using Django REST Framework.

### Changed

- Refactored javascript libraries.
- Replaced basket handling via old API endpoints with django REST framework
  calls.

- Replaced django-click dependency with django native command handling.
- Set limit (1000) for variables associated to a basket to improve server performance.

## [4.2.4] - 2020-02-27

### Changed

- Updated django from 2.2.10 to 3.0.3

### Fixed

- Added missing migration.
- crash occurring while trying to display faulty dataset data.

## [4.2.3] - 2020-02-24

### Changed

- Badge with news on Homepage is now dynamically filled from the database.
- Limit LabelTable size to fix system overloading.
- Variable detail `description` is now filled from the database field
  `description`. Was formerly filled from `description_long`.

### Removed

- fakeredis from dependencies.

## [4.2.2] - 2020-01-16

### Changed

- Update "legacy" import to work with image import.
- Major refactoring of variable model.

### Fixed

- Comply to new names used in ReactiveList of reactivesearch-vue.
- pytest-mock is no longer used as a context manager.

  - Newest release of pytest-mocker raises
    an error if used as context manager.

- Update workspace.management.commands.restore to work with updates in new (external)
  tablib version.

## [4.2.1] - 2019-11-20

### Changed

- Image Import

  - Handle urls, where no image can be retrieved.
  - Do not load images larger than 200KB.

- Patch old import to work with questions_images.csv

### Fixed

- Instrument import passed wrong object to image import.

## [4.2.0] - 2019-10-31

### Changed

- BasketVariables are no longer deleted when their corresponding variables
  are deleted.

  - Function was implemented to clean up stale BasketVariables if the need arises.

- Copyright notice to include former contributors.
- dev: NGINX now set up for debugging long requests.
- dev: Setup now better supports commit signing.
- Landing page for successful password reset was changed.

  - It now extends the standard registration template.
  - This extension adds a badge with a success message.

- Switch to Python 3.8 from 3.7.

### Fixed

- dev: Move pytest coverage flags from setup.cfg to .travis.yml.
- - Coverage Reports in Pytest versions newer than 5.0.1
    did cause issues with the vscode debugger.
- dev: Pylint Pre-commit hook properly uses pylint_django plugin.
- sort_id for variable imports is now incremented for each variable.

  - Before it was only set to 1 for each variable.

## [4.1.2] - 2019-10-07

### Fixed

- Version pin of postfix for docker postfix image is less strict.

  - apk was not able to install pinned version for the newest alpine version.

## [4.1.1] - 2019-10-01

### Added

- Function to alter result text above search results (x results found in yms)

  - Now adds "More than " if result count is higher than the elasticsearch 7 scroll limit
    of 10000. Meaning it will display "More than 10000 results found in yms".

### Changed

- Update several dependencies.

### Fixed

- Installation of dependencies for the dev container and travis setup.

  - Setup only installed dev dependencies without the applications dependencies.

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
  >

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

[unreleased]: https://github.com/ddionrails/ddionrails/compare/v4.6.1...develop
[4.6.1]: https://github.com/ddionrails/ddionrails/compare/v4.6.0...v4.6.1
[4.6.0]: https://github.com/ddionrails/ddionrails/compare/v4.5.4...v4.6.0
[4.5.4]: https://github.com/ddionrails/ddionrails/compare/v4.5.3...v4.5.4
[4.5.3]: https://github.com/ddionrails/ddionrails/compare/v4.5.2...v4.5.3
[4.5.2]: https://github.com/ddionrails/ddionrails/compare/v4.5.1...v4.5.2
[4.5.1]: https://github.com/ddionrails/ddionrails/compare/v4.5.0...v4.5.1
[4.5.0]: https://github.com/ddionrails/ddionrails/compare/v4.4.3...v4.5.0
[4.4.3]: https://github.com/ddionrails/ddionrails/compare/v4.4.2...v4.4.3
[4.4.2]: https://github.com/ddionrails/ddionrails/compare/v4.4.1...v4.4.2
[4.4.1]: https://github.com/ddionrails/ddionrails/compare/v4.4.0...v4.4.1
[4.4.0]: https://github.com/ddionrails/ddionrails/compare/v4.3.0...v4.4.0
[4.3.0]: https://github.com/ddionrails/ddionrails/compare/v4.2.4...v4.3.0
[4.2.4]: https://github.com/ddionrails/ddionrails/compare/v4.2.3...v4.2.4
[4.2.3]: https://github.com/ddionrails/ddionrails/compare/v4.2.2...v4.2.3
[4.2.2]: https://github.com/ddionrails/ddionrails/compare/v4.2.1...v4.2.2
[4.2.1]: https://github.com/ddionrails/ddionrails/compare/v4.2.0...v4.2.1
[4.2.0]: https://github.com/ddionrails/ddionrails/compare/v4.1.2...v4.2.0
[4.1.2]: https://github.com/ddionrails/ddionrails/compare/v4.1.1...v4.1.2
[4.1.1]: https://github.com/ddionrails/ddionrails/compare/v4.1.0...v4.1.1
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

# Paneldata

[![Python version][python-badge]](https://www.python.org/downloads/release/python-3131/)
[![Django version][django-badge]](https://docs.djangoproject.com/en/5.1/releases/5.1.4/)
[![Repo license][license-badge]](https://www.gnu.org/licenses/agpl-3.0)

![System-Tests](https://github.com/ddionrails/ddionrails/actions/workflows/system-tests.yml/badge.svg)
[![Issues][issues-badge]](https://github.com/ddionrails/ddionrails/issues/)
[![Codecov][codecov-badge]](https://codecov.io/gh/ddionrails/ddionrails)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0af735a0e3664fdb85ea6c92c99fe25f)](https://www.codacy.com/gh/ddionrails/ddionrails/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ddionrails/ddionrails&amp;utm_campaign=Badge_Grade)

Paneldata is a server solution to make panel study meta data more accessible.

## Table of contents

- [Paneldata](#paneldata)
  - [Table of contents](#table-of-contents)
  - [Contributions](#contributions)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installing](#installing)
      - [Development Environment](#development-environment)
      - [Production Environment](#production-environment)
    - [Importing Data](#importing-data)
  - [Running the tests](#running-the-tests)
  - [Versioning](#versioning)
  - [GNU AGPL-3.0](#gnu-agpl-30)


## Contributions

Please see our [CONTRIBUTING.md](.github/CONTRIBUTING.md),
if you want to contribute to this project.

## Getting Started

### Prerequisites

Follow the installation instructions for the Docker Engine:

- <https://docs.docker.com/engine/install/>

To verify the installation was successful, you can type:

```bash
$ docker --version
Docker version 27.5.1, build 9f9e405
```

### Installing

#### Development Environment

Clone the repository

```bash
git clone https://github.com/ddionrails/ddionrails.git
cd ddionrails/
```

To start up a default development setup use the base compose file together with the docker-compose-remote-dev.yml

```bash
docker compose -f "docker-compose.yml" -f "docker-compose-remote-dev.yml" up -d
```

Using Visual Studio Code will make the process even simpler.
Just open the project after installing the
[remote development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
plugin.
VSCode will prompt you to reopen it in the
development container.
When confirmed, VSCode will set up all services for development through `docker-compose`.

With the basic setup the development container will be available at `localhost`.

:warning: **Warning** Do not use this in production the settings used by
the dev compose files are not secure.
This is also the reason why there is no docker-compose.override.yml
provided with the repository. These settings should not accidentally find their
way into production.

#### Production Environment

**Before** starting the services via docker compose:

- \[Optional\] Benchmark your docker setup with
  [docker-bench-security](https://github.com/docker/docker-bench-security).

  - Some of the changes needed to secure your docker setup might lead 
    to loss of containers and volumes. It would be better to make the
    changes before creating any containers on the system.

- Customize the environment files in docker/environments/
  and rename them to remove example from their name.

  - database.env should contain secure password.
  - django.env should be set up for production or staging

    - DJANGO_DEBUG should always be False for Production
    - DJANGO_SECRET_KEY should be long and random
    - ALLOWED_HOSTS should match your setup
    - DEFAULT_FROM_EMAIL is the address password reset emails will be send from.
    - FEEDBACK_TO_EMAILS is a list of Email adresses where feedback is supposed
      to be send to. List entries are separated by , and each entry contains a purpose
      and an email address separated by :. There are currently two 
      feedback form purposes: search and statistics.


- Remove the comment in the environment blocks in the
  docker compose file to load the environment files.
  Or create a docker-compose.override.yml file that sets
  the environment files.
- Customize the docker/nginx/nginx.example.conf and rename it to nginx.conf.

  - Sections that need to be changed are marked with `REPLACE_ME`
  - For ssl change your docker-compose.yml or docker-compose.override.yml
    to mount cert and key at the right location.

    - If you use a ca-chain file, add this file to the end of your crt file.
      This file can then be used by nginx as certificate.

- \[Optional\] Set up a backup routine for the database.

### Importing Data

To import a study's metadata into the system, you need a git repository
containing a couple of .csv and .json files (e.g. <https://github.com/ddionrails/testsuite/tree/master/ddionrails>).

You need to add your study to the system by invoking the `add` command:

```bash
docker compose exec web python manage.py add soep-test github.com/ddionrails/testsuite
```

You clone or pull the repository with `update`:

```bash
docker compose exec web python manage.py update soep-test
```

Your study's metadata gets inserted into the database by adding import jobs onto
a Redis queue (this can take some time). The last job includes indexing all
metadata into the Elasticsearch indices.

Summary:

```bash
docker compose exec web python manage.py add soep-test github.com/ddionrails/testsuite
docker compose exec web python manage.py update
```

## Running the tests

To run the unit and integration tests you can call `paver test`.
This does not run functional tests with Selenium.

```bash
cd ddionrails/
docker compose -f "docker-compose.yml" -f "docker-compose-dev.yml" up -d
docker compose exec web paver test
```

## Versioning

For the versions available, either look at the
[tags of this repository](https://github.com/ddionrails/ddionrails/tags)
or at the [changelog](CHANGELOG.md).

This project adheres to [Semantic Versioning 2.0.0](https://semver.org/).

## GNU AGPL-3.0

This project is licensed under the GNU AGPL-3.0 License -see the
[LICENSE.md](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
file for details

<!-- Markdown link & img dfn's -->

[python-badge]: https://img.shields.io/badge/Python-3.13.1-blue.svg
[django-badge]: https://img.shields.io/badge/Django-5.1.4-blue.svg
[license-badge]: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
[codecov-badge]: https://img.shields.io/codecov/c/github/ddionrails/ddionrails.svg
[travis-badge]: https://img.shields.io/travis/ddionrails/ddionrails.svg
[issues-badge]: https://img.shields.io/github/issues/ddionrails/ddionrails.svg
[codacy-badge]: https://api.codacy.com/project/badge/Grade/0382ce2fae284b608bfba7bc2da74a4b

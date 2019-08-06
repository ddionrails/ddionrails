# DDI on Rails

[![Python version][python-badge]](https://www.python.org/downloads/release/python-374/)
[![Django version][django-badge]](https://docs.djangoproject.com/en/2.2/releases/2.2.4/)
[![Repo license][license-badge]](https://www.gnu.org/licenses/agpl-3.0)

[![Issues][issues-badge]](https://github.com/ddionrails/ddionrails/issues/)
[![Travis][travis-badge]](https://travis-ci.org/ddionrails/ddionrails/)
[![Codecov][codecov-badge]](https://codecov.io/gh/ddionrails/ddionrails)
[![Codacy][codacy-badge]](https://app.codacy.com/project/ddionrails/ddionrails/dashboard)

The data portal DDI on Rails accompanies researchers throughout the entire
course of their research projects from conception to publication/citation.

The system offers researchers the possibility to explore the data, to compile
personalized datasets, and to publish results on the publication database.

In contrast to similar products, DDI on Rails is study-independent and
open-source, is able to document data with multiple versions/distributions and
the specific characteristics of a longitudinal study, and is easy to use.

## Table of contents

* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installing](#installing)
    * [Development Environment](#development-environment)
    * [Production Environment](#production-environment)
  * [Importing Data](#importing-data)
* [Running the tests](#running-the-tests)
* [Versioning](#versioning)
* [GNU AGPL-3.0](#gnu-agpl-30)

## Getting Started

### Prerequisites

Follow the installation instructions for Docker and Docker-Compose:

- <https://docs.docker.com/install/>
- <https://docs.docker.com/compose/install/>

To verify the installation was successful, you can type:

``` bash
$ docker --version
Docker version 18.09.5, ...
$ docker-compose --version
docker-compose version 1.24.0, ...
```

### Installing

#### Development Environment

Clone the repository

``` bash
git clone https://github.com/ddionrails/ddionrails.git
cd ddionrails/
```

Build the Docker images and start containers with development setings

``` bash
docker-compose -f "docker-compose.yml" -f "docker-compose-dev.yml" build
```

:warning: __Warning__ Do not use this in production the settings in
`docker-compose-dev.yml` are not secure.

#### Production Environment

__Before__ starting the services via docker-compose:

- Customize the environment files in docker/environments/
  and rename them to remove example from their name.

  - database.env should contain secure password.
  - django.env should be set up for production or staging

    - DJANGO_DEBUG should always be False for Production
    - DJANGO_SECRET_KEY should be long and random
    - ALLOWED_HOSTS should match your setup

- Uncomment the environment blocks in the
  docker-compose file to load the environment files.
- Or create a docker-compose.override.yml file containing
  the environment files.
- Customize the docker/nginx/nginx.example.conf and rename it to nginx.conf.

  - Sections that need to be changed are marked with `REPLACE_ME`
  - For ssl change your docker-compose.yml or docker-compose.override.yml
    to mount cert and key at the right location.

    - If you use a ca-chain file add this file to the end of your crt file.
      This file can then be used by nginx as certificate.

- Optional: Set up a backup routine for the database.

__After__ starting the services via docker-compose:

- A mapping needs to be loaded into elasticsearch in order
  for all search interfaces to work. :frowning_face:
- Enter the django container via
  `docker-compose exec web python manage.py index create`
- The elasticsearch index is kept in a named volume,
  meaning that the mapping is kept even through container recreations.

### Importing Data

To import a study's metadata into the system, you need a git repository
containing a couple of .csv and .json files (e.g. <https://github.com/ddionrails/testsuite/tree/master/ddionrails>).

You need to add your study to the system by invoking the `add` command:

``` bash
docker-compose exec web python manage.py add soep-test github.com/ddionrails/testsuite
```

You clone or pull the repository with `update`:
``` bash
docker-compose exec web python manage.py update soep-test
```

Your study's metadata gets inserted into the database by adding import jobs onto
a Redis queue (this can take some time).

To index your study's metadata into Elasticsearch you use the `index` command:
``` bash
docker-compose exec web python manage.py index populate
```

Summary:
``` bash
docker-compose exec web python manage.py add soep-test github.com/ddionrails/testsuite
docker-compose exec web python manage.py update
docker-compose exec web python manage.py index populate
```

## Running the tests

To run the unit and integration tests you can call `paver test`.
This does not run functional tests with Selenium.

``` bash
cd ddionrails/
docker-compose -f "docker-compose.yml" -f "docker-compose-dev.yml" up -d
docker-compose exec web paver test
```

## Versioning

For the versions available, see the
[tags on this repository](https://github.com/ddionrails/ddionrails/tags).

## GNU AGPL-3.0

This project is licensed under the GNU AGPL-3.0 License -see the
[LICENSE.md](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md)
file for details

<!-- Markdown link & img dfn's -->

[python-badge]: https://img.shields.io/badge/Python-3.7.4-blue.svg
[django-badge]: https://img.shields.io/badge/Django-2.2.4-blue.svg
[license-badge]: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
[codecov-badge]: https://img.shields.io/codecov/c/github/ddionrails/ddionrails.svg
[travis-badge]: https://img.shields.io/travis/ddionrails/ddionrails.svg
[issues-badge]: https://img.shields.io/github/issues/ddionrails/ddionrails.svg
[codacy-badge]: https://api.codacy.com/project/badge/Grade/0382ce2fae284b608bfba7bc2da74a4b

# DDI on Rails – version 2

[![Python version][python-badge]](https://www.python.org/downloads/release/python-373releases/)
[![Django version][django-badge]](https://docs.djangoproject.com/en/2.2/)
[![Repo license][license-badge]](https://www.gnu.org/licenses/agpl-3.0)

[![Issues][issues-badge]](https://github.com/ddionrails/ddionrails/issues/)
[![Travis][travis-badge]](https://travis-ci.org/ddionrails/ddionrails/)
[![Codecov][codecov-badge]](https://codecov.io/gh/ddionrails/ddionrails)
[![Codacy][codacy-badge]](https://app.codacy.com/project/ddionrails/ddionrails/dashboard)
[![PyUp][pyup-badge]](https://pyup.io/repos/github/ddionrails/ddionrails/)
[![Greenkeeper][greenkeeper-badge]](https://greenkeeper.io/)

[![Repo size][reposize-badge]][reposize-badge]

The data portal DDI on Rails accompanies researchers throughout the entire course of their research projects from conception to publication/citation.

The system offers researchers the possibility to explore the data, to compile personalized datasets, and to publish results on the publication database.

In contrast to similar products, DDI on Rails is study-independent and open-source, is able to document data with multiple versions/distributions and the specific characteristics of a longitudinal study, and is easy to use.

## Getting Started

### Prerequisites

Follow the installation instructions for Docker and Docker-Compose:

- <https://docs.docker.com/install/>
- <https://docs.docker.com/compose/install/>

To verify the installation was successful, you can type:
```
$ docker --version
Docker version 18.09.5, ...
$ docker-compose --version
docker-compose version 1.24.0, ...
```

### Installing

#### Developement Environment

Clone the repository

```
$ git clone https://github.com/ddionrails/ddionrails.git
$ cd ddionrails/
```

Build the Docker images and start containers with developement setings

```
$ docker-compose -f "docker-compose.yml" -f "docker-compose-dev.yml" build
```

:warning: __Warning__ Do not use this in production the settings in `docker-compose-dev.yml` are not secure.

#### Production Environment

Before starting the services via docker-compose:

- Customize the environment files in docker/environments/ and rename them to remove example from their name.
  - database.env should contain secure password.
  - django.env should be set up for production or staging
    - DJANGO_DEBUG should always be False for Production
    - DJANGO_SECRET_KEY should be long and random
    - ALLOWED_HOSTS should match your setup
- Uncomment the environment blocks in the docker-compose file to load the environment files.
- Or create a docker-compose.override.yml file containing the environment files. 
- Customize the docker/nginx/nginx.example.conf and rename it to nginx.conf.
  - Sections that need to be changed are marked with `REPLACE_ME`
  - For ssl change your docker-compose.yml or docker-compose.override.yml to mount cert and key at the right location.
   - If you use a ca-chain file add this file to the end of your crt file. This file can then be used by nginx as certificate.
- Optional: Set up a backup routine for the database.
  

## Running the tests

```
$ cd ddionrails/
$ docker-compose -f "docker-compose.yml" -f "docker-compose-dev.yml" up -d
$ docker-compose -f "docker-compose.yml" -f "docker-compose-dev.yml" exec web pytest
```

## Versioning

For the versions available, see the [tags on this repository](https://github.com/ddionrails/ddionrails/tags).

## License

This project is licensed under the GNU AGPLv3 License - see the [LICENSE.md](https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md) file for details

<!-- Markdown link & img dfn's -->

[python-badge]: https://img.shields.io/badge/Python-3.7.3-blue.svg
[django-badge]: https://img.shields.io/badge/Django-2.2-blue.svg
[license-badge]: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
[reposize-badge]: https://img.shields.io/github/repo-size/badges/shields.svg
[codecov-badge]: https://img.shields.io/codecov/c/github/ddionrails/ddionrails.svg
[travis-badge]: https://img.shields.io/travis/ddionrails/ddionrails.svg
[pyup-badge]: https://pyup.io/repos/github/ddionrails/ddionrails/shield.svg
[greenkeeper-badge]: https://badges.greenkeeper.io/greenkeeperio/badges.svg
[issues-badge]: https://img.shields.io/github/issues/ddionrails/ddionrails.svg
[codacy-badge]: https://api.codacy.com/project/badge/Grade/0382ce2fae284b608bfba7bc2da74a4b

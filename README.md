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

```
$ sudo apt-get install redis-server
$ sudo apt-get install git
$ sudo apt-get install graphviz
$ sudo apt-get install nodejs
```

### Installing

Clone the repository

```
$ git clone https://github.com/ddionrails/ddionrails.git
$ cd ddionrails/
```

Install Python 3.6 and 3.6-dev packages.

```
$ sudo apt-get install -y python3.6 python3.6-dev python3-pip
$ pip install --upgrade --user pip wheel pipenv
```

### Deployment using pipenv

Install all packages and dev packages in ddionrails.

```
$ pipenv install --dev
Installing dependencies from Pipfile.lock (d00398)…
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 85/85 — 00:00:26
```

Activate the virtual environment

```
$ pipenv shell
(ddionrails) $
```

Verify e.g. Django is installed

```
(ddionrails) $ django-admin --version
2.1.7
```

Install Elasticsearch

```
(ddionrails) $ paver install_elastic
```

Install front-end-dependencies

```
(ddionrails) $ paver setup_frontend
```

For development: copy default secrets.json

```
(ddionrails) $ paver copy_secrets_file
```

Make migrations

```
(ddionrails) $ paver migrate
```

Start server, elastic and rqworker each in one terminal with pipenv

```
$ pipenv shell
(ddionrails) $ paver server
```

```
$ pipenv shell
(ddionrails) $ paver elastic
```

```
$ pipenv shell
(ddionrails) $ paver rqworker
```

## Running the tests

```
$ cd ddionrails/
$ pipenv install --dev
$ pipenv shell
(ddionrails) $ pytest
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

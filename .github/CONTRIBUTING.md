# Contributing to ddionrails

Thank you for reading this and thank you for wanting to contribute.

In order to keep the codebase healthy and maintainable for us, we would like to
set some guidelines in the following text.

# Table of Contents

[Contributions](#contributions)

  + [Reporting Bugs](#reporting-bugs)
  + [Suggesting Enhancements](#suggesting-enhancements)
  + [Code Contributions](#code-contributions)
    - [Code Quality](#code-quality)
      - [Testing](#testing)
      - [Code Style](#code-style)

# Contributions

## Reporting Bugs

Problems in the project's code can be reported as
[issues](https://github.com/ddionrails/ddionrails/issues).
Before opening a new issue, please do a cursory search to see if the problem was
not already reported.
Feel free to leave a helpful comment if you find an issue, that describes your problem.

We have template in the [issue creation](https://github.com/ddionrails/ddionrails/issues/new)
interface to help you with formulating your problem. In addition please provide a
clear and descriptive title for the issue.
Including images in the issue can also be of great help.

## Suggesting Enhancements

As with [bugs](#reporting-bugs), please take a look if your suggestion already exists
as an [issue](https://github.com/ddionrails/ddionrails/issues).

Please remove the parts of the template, that is intended for bug reports
if you make a feature suggestion.

We are always open for new ideas but some features might not fit into the current
architecture, the current goals or require a work load, 
that is too high.
It may take us some time to evaluate the issue but we will give feedback if and how 
a new feature request could be implemented.

## Code Contributions

To contribute, please create a topic branch from develop. Do this here or on a 
fork of this repository, depending on your affiliation with the project.

### Code Quality

Additions to the code base have to follow the quality standards set for this project.
Tools to guarantee the code quality are included with the dev dependencies in the
Pipfile and package.json.
Use `pre-commit install` to setup pre-commit.
It will check your code before every commit.
You might have to disable the unit test hook by setting the environment variable
 `export SKIP=unittest` , depending on your setup.

#### Testing

New code has to include tests, that guarantee the functionality of the implementation.
If old code is modified, tests might also need to be modified.
Tests are run with pytest on [travis-ci](https://travis-ci.org/ddionrails/ddionrails).

Please take a look inside the `tests` folder inside the root of the repository to
get an idea how tests should look like. The folder structure mirrors that of the actual
code in the `ddionrails` folder.

#### Code Style

Some of the tools included in the dev dependencies can help you follow this project's 
coding style.
Configurations for the development tools can be found in setup.cfg, package.json and
pyproject.toml. You can check the .pre-commit-config.yaml if you are unsure on how to 
call the tools with their config.

Python code should comply to most of [PEP 8](https://www.python.org/dev/peps/pep-0008/).
Line length should be set of a maximum of 90 instead of 80.
Use pylint and bandit to check if your code is up to standard.
Imports should be sorted in accordance with isort.

Javascript should be checked with ESLint.

Please comment your code in accordance with the Google style guides for
[Python](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
and [Javascript](https://google.github.io/styleguide/jsguide.html#jsdoc).
Use Python [type hints](https://www.python.org/dev/peps/pep-0484/) wherever possible
and import [typing](https://docs.python.org/3/library/typing.html) if necessary.
Type declaration inside the Python doc string can consequently be omitted.

The project's code style is automatically checked via
[Codacy](https://app.codacy.com/project/ddionrails/ddionrails/dashboard).
Code that introduces new issues will not be pulled.


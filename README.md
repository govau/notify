[![Build Status](https://api.travis-ci.org/alphagov/notifications-utils.svg?branch=master)](https://api.travis-ci.org/alphagov/notifications-utils.svg?branch=master)


# GOV.UK Notify - notifications-utils [BETA]
Shared python code for GOV.UK Notify

Provides logging utils etc.

## Installing

This is a [python](https://www.python.org/) application.

#### Python version
This is a python 3 application. It has not been run against any version of python 2.x

    brew install python3

#### Dependency management

This is done through [pip](pip.readthedocs.org/) and [virtualenv](https://virtualenv.readthedocs.org/en/latest/). In practise we have used
[VirtualEnvWrapper](http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html) for our virtual environemnts.

Setting up a virtualenvwrapper for python3

    mkvirtualenv -p /usr/local/bin/python3 notifications-python-client


The boostrap script will set the application up. *Ensure you have activated the virtual environment first.*

    ./scripts/bootstrap.sh

This will

* Use pip to install dependencies.

#### Tests

The `./scripts/run_tests.py` script will run all the tests. [py.test](http://pytest.org/latest/) is used for testing.

Running tests will also apply syntax checking, using [pycodestyle](https://pypi.python.org/pypi/pycodestyle).

Additionally code coverage is checked via pytest-cov:

[![Requirements Status](https://requires.io/github/alphagov/notifications-api/requirements.svg?branch=master)](https://requires.io/github/alphagov/notifications-api/requirements/?branch=master)
[![Coverage Status](https://coveralls.io/repos/alphagov/notifications-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/alphagov/notifications-api?branch=master)

# notifications-api

Notifications api
Application for the notification api.

Read and write notifications/status queue.
Get and update notification status.

## Setting Up

### Pipenv

install pipenv according to your platform. it can be installed through
homebrew, apt, or most easily-- pip.

```shell
    pip3 install --user pipenv
```

### `.env`

copy .env.sample to a file called `.env` and fill in the missing values with the
help of a colleague. Pipenv will read from this file in development

NOTES:

* Replace the placeholder key and prefix values as appropriate
* The SECRET_KEY and DANGEROUS_SALT should match those in the [notifications-admin](https://github.com/alphagov/notifications-admin) app.
* The unique prefix for the queue names prevents clashing with others' queues in shared amazon environment and enables filtering by queue name in the SQS interface.

### Postgres

Install postgres. this can be done easily through homebrew

```shell
    brew install postgres
    brew services start postgresql
```

## To run the application

First, create a postgres database with the command `createdb notification_api`.

Then, run `make setup` to install dependencies.

, set up your environment, and
initialise the database.

You can run make `setup-db` whenever you need to update your database in response
to migrations.

You need to run the api application and a local celery instance.

```shell
    make run
```

```shell
    make run-celery
```

## To test the application

First, ensure that `make setup` has been run, as it updates the test database

Then simply run

```shell
    make test
```

That will run flake8 for code analysis and our unit test suite.

## To run one off tasks

Tasks are run through the `flask` command - run `pipenv run flask --help` for more information. There are two sections we need to
care about: `pipenv run flask db` contains alembic migration commands, and `pipenv run flask command` contains all of our custom commands.

All commands and command options have a --help command if you need more information.

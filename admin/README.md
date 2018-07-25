# notifications-admin

GOV.AU Notify admin application.

## Features of this application

- Register and manage users
- Create and manage services
- Send batch emails and SMS by uploading a CSV
- Show history of notifications

## First-time setup

Languages needed

- Python 3.6+
- [Node](https://nodejs.org/) 5.0.0 or greater
- [npm](https://www.npmjs.com/) 3.0.0 or greater

```shell
    brew install node
```

The app runs within a virtual environment. We use pipenv for easier environment
management

```shell
    pip3 install --user pipenv
```

Install dependencies and build the frontend assets:

```shell
    make-setup
```

## Rebuilding the frontend assets

If you want the front end assets to re-compile on changes, leave this running
in a separate terminal from the app

```shell
    make run-gulp
```

## Create a local `.env` by copying .env.sample

copy the `.env.sample` file to a new file called `.env`. Pipenv will load this
when it runs commands.

## Running the application

```shell
    make run
```

Then visit [localhost:6012](http://localhost:6012)

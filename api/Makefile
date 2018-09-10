GUNICORN ?= gunicorn
PIPENV ?= pipenv
TEST_PIPENV_DOTENV_LOCATION ?= $(shell pwd)/.env_test
RUNNER ?= $(PIPENV) run
PORT   ?= 6011
WORKERS?= 4
CF     ?= cf
APP    ?= notify-api
STG    ?= dev

export PIPENV_DOTENV_LOCATION

.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

APP_VERSION_FILE = app/version.py
GIT_COMMIT ?= $(shell git rev-parse HEAD)
BUILD_NUMBER ?= 0
BUILD_URL ?=

DOCKER_CONTAINER_PREFIX = ${USER}-

DOCKER_TEST_DB_PORT ?= 5420

APP_DIRS  = $(shell find tests/app/* -maxdepth 1 -type d)
APP_TESTS = $(APP_DIRS:tests/app/%=test-%)

DAO_DIRS  = $(shell find tests/app/dao/* -maxdepth 1 -type f)
DAO_TESTS = $(DAO_DIRS:tests/app/dao/%=test-dao-%)


# A help target including self-documenting targets (see the awk statement)
define HELP_TEXT
Usage: make [TARGET]... [MAKEVAR1=SOMETHING]...

Available targets:
endef
export HELP_TEXT
help: ## List common commands and their usage
	@echo "notify-api"
	@echo
	@echo "$$HELP_TEXT"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)


${APP_VERSION_FILE}:
	@echo -e "__commit_sha__ = \"${CIRCLE_SHA1}\"\n__time__ = \"${DATE}\"\n__build_job_number__ = \"${CIRCLE_BUILD_NUM}\"\n__build_job_url__ = \"${CIRCLE_BUILD_URL}\"" > $@

version-file: ${APP_VERSION_FILE}

Pipfile Pipfile.lock:
	$(PIPENV) install

setup: ## Setup virtualenv and install python dependencies
	$(PIPENV) install

setup-dev: ## Setup everything in dev mode for testing
	$(PIPENV) install --dev

setup-db: version-file ## Run database migrations
	$(RUNNER) flask db upgrade

setup-test-db:
	$(MAKE) setup-db

test: lint tests

lint:
	$(RUNNER) flake8 .

tests: PIPENV_DOTENV_LOCATION := $(TEST_PIPENV_DOTENV_LOCATION)
tests: version-file
	$(MAKE) setup-test-db
	$(RUNNER) py.test -n4 $(PYTEST_ARGS) tests

$(APP_TESTS): test-%: version-file
$(APP_TESTS): PIPENV_DOTENV_LOCATION := $(TEST_PIPENV_DOTENV_LOCATION)
$(APP_TESTS):
	$(MAKE) setup-test-db
	$(RUNNER) py.test -n4 $(PYTEST_ARGS) tests/app/$*

$(DAO_TESTS): test-dao-%: version-file
$(DAO_TESTS): PIPENV_DOTENV_LOCATION := $(TEST_PIPENV_DOTENV_LOCATION)
$(DAO_TESTS):
	$(MAKE) setup-test-db
	$(RUNNER) py.test -n4 $(PYTEST_ARGS) tests/app/dao/$*

test-roots: PIPENV_DOTENV_LOCATION := $(TEST_PIPENV_DOTENV_LOCATION)
test-roots: version-file
	$(MAKE) setup-test-db
	$(RUNNER) py.test -n4 $(PYTEST_ARGS) tests/app/*.py

wait-for-docker-test-db:
	@number=1 ; while [[ $$number -le 10 ]] ; do \
		nc -z localhost $(DOCKER_TEST_DB_PORT) && echo Success && exit 0 ; \
		echo -n . ; \
		sleep 1 ; \
        ((number = number + 1)) ; \
    done ; \
	echo Failed waiting for Postgres && exit 1

create-docker-test-db:
	docker rm -f $(DOCKER_CONTAINER_PREFIX)notify-test-db 2> /dev/null || true
	@docker run -d \
		--name "$(DOCKER_CONTAINER_PREFIX)notify-test-db" \
		-p $(DOCKER_TEST_DB_PORT):5432 \
		-e POSTGRES_PASSWORD="" \
		-e POSTGRES_DB="test_notification_api" \
		postgres:9.6

	$(MAKE) wait-for-docker-test-db;

run: version-file ## Run a development server (reloading)
	$(RUNNER) flask run -p $(PORT)

run-gunicorn: version-file ## Run a production server
	$(RUNNER) $(GUNICORN) -w $(WORKERS) -b 0.0.0.0:$(PORT) -k eventlet application

run-celery: version-file ## Run background workers
	$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO

run-ngrok:
	ngrok http 6011

pipenv-requirements.txt: Pipfile.lock
	$(PIPENV) lock -r > $@

vendor: pipenv-requirements.txt
	$(RUNNER) pip download -d $@ -r $<

native-vendor:
	mkdir -p $@

build-linux-wheels: pipenv-requirements.txt native-vendor
	cat $< | $(RUNNER) python scripts/fixup-requirements.py --ignore | docker run\
		-i --rm\
		-v $(shell pwd)/build-linux-wheels.sh:/build-linux-wheels.sh\
		quay.io/pypa/manylinux1_x86_64 bash /build-linux-wheels.sh | tar -C native-vendor -x

requirements.txt: pipenv-requirements.txt
	cat $< | $(RUNNER) python scripts/fixup-requirements.py > $@

run-production: setup-db ## Apply migrations and run production server
	$(MAKE) run-gunicorn

manifest-vars-%.yml:
	echo "stg: $*" > $@

deploy: vendor requirements.txt ## Deploy prod application
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: manifest-vars-$(STG).yml vendor requirements.txt
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file $<

deploy-celery:
	APP=notify-celery $(MAKE) deploy

deploy-dev-celery:
	APP=notify-celery $(MAKE) deploy-dev

create-migration: MIGRATION_NUMBER  ?= $(shell $(RUNNER) flask db current | $(RUNNER) python scripts/next_revision.py)
create-migration: MIGRATION_MESSAGE ?= $(shell bash -c 'read -p "Migration message: " message; echo $$message')
create-migration: ## Create an appropriately ordered migration stub
	$(RUNNER) flask db revision --rev-id $(MIGRATION_NUMBER) --message "$(MIGRATION_MESSAGE)"

.PHONY:
	setup setup-dev setup-db \
	setup-test-db test lint tests $(APP_TESTS) $(DAO_TESTS) test-roots \
	run run-celery \
	deploy deploy-api deploy-celery \
	run-production \
	create-migration help

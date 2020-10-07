GUNICORN ?= gunicorn
PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run
PORT   ?= 6011
WORKERS?= 4
CF     ?= cf
APP    ?= notify-api
STG    ?= development

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

install: version-file ## Setup virtualenv and install python dependencies
	$(PIPENV) install

install-dev: ## Setup everything in dev mode for testing
	$(PIPENV) install --dev

setup-db: version-file ## Run database migrations
	$(RUNNER) flask db upgrade

setup-test-db:
	$(MAKE) setup-db

test: lint tests

lint:
	$(RUNNER) flake8 .

fmt:
	$(RUNNER) autopep8 --in-place --recursive .

check-vulnerabilities:
	$(RUNNER) bandit -c bandit.yml -x migration -r . -l

tests: version-file
	$(RUNNER) pytest -n4 $(PYTEST_ARGS) tests

$(APP_TESTS): test-%: version-file
	$(RUNNER) pytest -n4 $(PYTEST_ARGS) tests/app/$*

$(DAO_TESTS): test-dao-%: version-file
	$(RUNNER) pytest -n4 $(PYTEST_ARGS) tests/app/dao/$*

test-roots: version-file
	$(RUNNER) pytest -n4 $(PYTEST_ARGS) tests/app/*.py

run: version-file ## Run a development server (reloading)
	$(RUNNER) flask run -p $(PORT)

run-gunicorn: version-file ## Run a production server
	$(RUNNER) $(GUNICORN) -w $(WORKERS) -b 0.0.0.0:$(PORT) -k sync application:application

run-celery-events:
	NOTIFY_CELERY_CMD=events \
		$(RUNNER) celery -A run_celery.notify_celery events

run-celery-worker: version-file ## Run background workers (all queues, useful for development)
	NOTIFY_CELERY_CMD=worker \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO

run-celery-worker-default: version-file ## Run background workers (default implies all other non-dedicated queues)
	NOTIFY_CELERY_CMD=worker-default \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-X priority-tasks,send-email-tasks,send-sms-tasks,service-callbacks,retry-tasks,notify-internal-tasks

run-celery-worker-priority: version-file ## Run background workers (priority queue)
	NOTIFY_CELERY_CMD=worker-priority \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-Q priority-tasks

run-celery-worker-sender: version-file ## Run background workers (send email and SMS queues)
	NOTIFY_CELERY_CMD=worker-sender \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-Q send-email-tasks,send-sms-tasks

run-celery-worker-callbacks: version-file ## Run background workers (service callbacks queue)
	NOTIFY_CELERY_CMD=worker-callbacks \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-Q service-callbacks

run-celery-worker-retrys: version-file ## Run background workers (retry tasks queue)
	NOTIFY_CELERY_CMD=worker-retrys \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-Q retry-tasks

run-celery-worker-internal: version-file ## Run background workers (Notify internal tasks queue)
	NOTIFY_CELERY_CMD=worker-internal \
		$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO \
			-Q notify-internal-tasks

run-celery-beat: version-file ## Run scheduled tasks
	NOTIFY_CELERY_CMD=beat \
		$(RUNNER) celery -A run_celery.notify_celery beat --loglevel=INFO

run-ngrok:
	ngrok http 6011

requirements.txt: Pipfile.lock
	$(PIPENV) lock -r > $@

build: requirements.txt

run-production: setup-db ## Apply migrations and run production server
	$(MAKE) run-gunicorn

manifest-vars-%.yml:
	echo "stg: $*" > $@

deploy: requirements.txt ## Deploy prod application
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: manifest-vars-$(STG).yml requirements.txt
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file $<

	$(MAKE) create-sap-oauth2-client

deploy-celery-worker-default:
	APP=notify-celery-worker-default $(MAKE) deploy

deploy-celery-worker-priority:
	APP=notify-celery-worker-priority $(MAKE) deploy

deploy-celery-worker-sender:
	APP=notify-celery-worker-sender $(MAKE) deploy

deploy-celery-worker-callbacks:
	APP=notify-celery-worker-callbacks $(MAKE) deploy

deploy-celery-worker-retrys:
	APP=notify-celery-worker-retrys $(MAKE) deploy

deploy-celery-worker-internal:
	APP=notify-celery-worker-internal $(MAKE) deploy

deploy-dev-celery-worker-default:
	APP=notify-celery-worker-default $(MAKE) deploy-dev

deploy-dev-celery-worker-priority:
	APP=notify-celery-worker-priority $(MAKE) deploy-dev

deploy-dev-celery-worker-sender:
	APP=notify-celery-worker-sender $(MAKE) deploy-dev

deploy-dev-celery-worker-callbacks:
	APP=notify-celery-worker-callbacks $(MAKE) deploy-dev

deploy-dev-celery-worker-retrys:
	APP=notify-celery-worker-retrys $(MAKE) deploy-dev

deploy-dev-celery-worker-internal:
	APP=notify-celery-worker-internal $(MAKE) deploy-dev

deploy-celery-beat:
	APP=notify-celery-beat $(MAKE) deploy

deploy-dev-celery-beat:
	APP=notify-celery-beat $(MAKE) deploy-dev

create-migration: MIGRATION_NUMBER  ?= $(shell $(RUNNER) flask db current | $(RUNNER) python scripts/next_revision.py)
create-migration: MIGRATION_MESSAGE ?= $(shell bash -c 'read -p "Migration message: " message; echo $$message')
create-migration: ## Create an appropriately ordered migration stub
	$(RUNNER) flask db revision --rev-id $(MIGRATION_NUMBER) --message "$(MIGRATION_MESSAGE)"

# this is a hack because CircleCI env variables are awful
export SAP_OAUTH2_CLIENT_ID ?= $(SAP_OAUTH2_CLIENT_ID_DEV)
export SAP_OAUTH2_CLIENT_SECRET ?= $(SAP_OAUTH2_CLIENT_SECRET_DEV)

create-sap-oauth2-client:
	@$(CF) run-task $(APP)-$(STG) '$$RUNNER flask command create-sap-oauth2-client -i $(SAP_OAUTH2_CLIENT_ID) -s $(SAP_OAUTH2_CLIENT_SECRET)'

clean:
	# nothing to do

.PHONY:
	install install-dev setup-db \
	setup-test-db test lint fmt tests $(APP_TESTS) $(DAO_TESTS) test-roots \
	run run-celery-worker run-celery-beat \
	run-celery-worker-default run-celery-worker-priority run-celery-worker-sender run-celery-worker-callbacks run-celery-worker-retrys run-celery-worker-internal \
	deploy deploy-api \
	deploy-dev-celery-worker-default deploy-dev-celery-worker-priority deploy-dev-celery-worker-sender deploy-dev-celery-worker-callbacks deploy-dev-celery-worker-retrys deploy-dev-celery-worker-internal \
	deploy-celery-beat deploy-dev-celery-beat \
	run-production \
	create-migration help clean check-vulnerabilities \
	create-sap-oauth2-client

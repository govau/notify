GUNICORN ?= gunicorn
PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run
PORT   ?= 6011
WORKERS?= 4

.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

APP_VERSION_FILE = app/version.py
GIT_COMMIT ?= $(shell git rev-parse HEAD)
BUILD_NUMBER ?= 0
BUILD_URL ?=

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
	@echo -e "__travis_commit__ = \"${GIT_COMMIT}\"\n__time__ = \"${DATE}\"\n__travis_job_number__ = \"${BUILD_NUMBER}\"\n__travis_job_url__ = \"${BUILD_URL}\"" > $@

version-file: ${APP_VERSION_FILE}

Pipfile Pipfile.lock:
	$(PIPENV) install

setup: ## Setup virtualenv and install python dependencies
	$(PIPENV) install

setup-db: version-file ## Run database migrations
	$(RUNNER) flask db upgrade

test: version-file ## Run linter and tests
	$(RUNNER) flake8 .
	$(RUNNER) py.test --cov=app --cov-report=term-missing tests/ --junitxml=test_results.xml -n4 -v --maxfail=10

run: version-file ## Run a development server (reloading)
	$(RUNNER) flask run -p $(PORT)

run-gunicorn: version-file ## Run a production server
	$(RUNNER) $(GUNICORN) -w $(WORKERS) -b 0.0.0.0:$(PORT) -k eventlet application

run-celery: version-file ## Run background workers
	$(RUNNER) celery -A run_celery.notify_celery worker --loglevel=INFO 

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

deploy-api: vendor requirements.txt ## Deploy API to cloudfoundry
	cf zero-downtime-push notify-api -f manifest.yml

deploy-celery: vendor requirements.txt ## Deploy celery to cloudfoundry
	cf zero-downtime-push notify-celery -f manifest.yml

create-migration: MIGRATION_NUMBER  ?= $(shell $(RUNNER) flask db current | $(RUNNER) python scripts/next_revision.py)
create-migration: MIGRATION_MESSAGE ?= $(shell bash -c 'read -p "Migration message: " message; echo $$message')
create-migration: ## Create an appropriately ordered migration stub
	$(RUNNER) flask db revision --rev-id $(MIGRATION_NUMBER) --message "$(MIGRATION_MESSAGE)"

.PHONY: setup setup-db run run-celery deploy deploy-api deploy-celery run-production create-migration help

PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run
NPM    ?= npm
PORT   ?= 6012
WORKERS?= 4
APP    ?= notify-admin

SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

# A help target including self-documenting targets (see the awk statement)
define HELP_TEXT
Usage: make [TARGET]... [MAKEVAR1=SOMETHING]...

Available targets:
endef
export HELP_TEXT
help: ## List common commands and their usage
	@echo "notify-admin"
	@echo
	@echo "$$HELP_TEXT"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

app/version.py:
	@echo -e "__travis_commit__ = \"${GIT_COMMIT}\"\n__time__ = \"${DATE}\"\n__travis_job_number__ = \"${BUILD_NUMBER}\"\n__travis_job_url__ = \"${BUILD_URL}\"" > $@

version-file: app/version.py

Pipfile Pipfile.lock:
	$(PIPENV) install

setup-frontend: ## Setup and build css
	$(NPM) install
	$(NPM) run build -- --production

setup: setup-frontend ## Setup virtualenv, install python deps, build css
	$(PIPENV) install

setup-dev: setup-frontend ## Setup everything in dev mode
	$(PIPENV) install --dev

test: version-file ## Run linter, python tests, node tests
	$(RUNNER) flake8 .
	$(RUNNER) isort --check-only -rc ./app ./tests
	$(RUNNER) py.test --cov=app --cov-report=term-missing tests/ --junitxml=test_results.xml -n4 --maxfail=10
	$(NPM) test

run-gulp: ## Continuously build css
	$(NPM) run watch

run: version-file ## Run a development server (reloading)
	$(RUNNER) flask run -p $(PORT)

run-gunicorn: version-file ## Run a production server
	$(RUNNER) gunicorn -w $(WORKERS) -b 0.0.0.0:$(PORT) -k eventlet application

pipenv-requirements.txt: Pipfile.lock
	$(PIPENV) lock -r > $@

vendor: pipenv-requirements.txt
	$(RUNNER) pip download -d $@ -r $<

requirements.txt: pipenv-requirements.txt
	cat $< | $(RUNNER) python scripts/fixup-requirements.py > $@

native-vendor:
	mkdir -p $@

build-linux-wheels: pipenv-requirements.txt native-vendor
	cat $< | $(RUNNER) python scripts/fixup-requirements.py --ignore | docker run\
		-i --rm\
		-v $(shell pwd)/build-linux-wheels.sh:/build-linux-wheels.sh\
		quay.io/pypa/manylinux1_x86_64 bash /build-linux-wheels.sh | tar -C native-vendor -x

deploy: vendor requirements.txt ## Deploy admin to cloudfoundry
	cf zero-downtime-push $(APP) -f manifest.yml

.PHONY: help test setup-frontend setup setup-dev run run-gunicorn deploy build-linux-wheels

PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run
NPM    ?= npm
PORT   ?= 6012
WORKERS?= 4
CF     ?= cf
APP    ?= notify
STG    ?= dev

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
	@echo -e "__commit_sha__ = \"${CIRCLE_SHA1}\"\n__time__ = \"${DATE}\"\n__build_number__ = \"${CIRCLE_BUILD_NUM}\"\n__build_job_url__ = \"${CIRCLE_BUILD_URL}\"" > $@

version-file: app/version.py

Pipfile Pipfile.lock:
	$(PIPENV) install

build-frontend:
	$(NPM) run build -- --production

setup-frontend: ## Setup and build css
	$(NPM) install
	$(MAKE) build-frontend

setup: setup-frontend version-file ## Setup virtualenv, install python deps, build css
	$(PIPENV) install

setup-dev: setup-frontend version-file ## Setup everything in dev mode
	$(PIPENV) install --dev

test: version-file ## Run linter, python tests, node tests
	$(RUNNER) flake8 .
	$(RUNNER) isort --check-only -rc ./app ./tests
	$(MAKE) tests
	$(NPM) test

tests: version-file
	$(RUNNER) py.test -n4 tests

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


manifest-vars-%.yml:
	echo "stg: $*" > $@

deploy: vendor requirements.txt ## Deploy admin to cloudfoundry
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: manifest-vars-$(STG).yml vendor requirements.txt ## Deploy admin to cloudfoundry
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file $<

.PHONY: help test tests setup-frontend setup setup-dev run run-gunicorn deploy build-linux-wheels

PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run
NPM    ?= npm
PORT   ?= 6012
WORKERS?= 4
APP    ?= notify-admin

SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

CLD_HOST   ?= y.cld.gov.au
CF_API     ?= https://api.system.$(CLD_HOST)
CF_ORG     ?= dta
CF_SPACE   ?= notifications

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: cf-login
cf-login:
	@cf login\
		-a "${CF_API}"\
		-u "${CF_USERNAME}"\
		-p "${CF_PASSWORD}"\
		-o "${CF_ORG}"\
		-s "${CF_SPACE}"

app/version.py:
	@echo -e "__travis_commit__ = \"${GIT_COMMIT}\"\n__time__ = \"${DATE}\"\n__travis_job_number__ = \"${BUILD_NUMBER}\"\n__travis_job_url__ = \"${BUILD_URL}\"" > $@

version-file: app/version.py

Pipfile Pipfile.lock:
	$(PIPENV) install

setup-frontend:
	$(NPM) install
	$(NPM) run build -- --production

setup: setup-frontend
	$(PIPENV) install

setup-dev: setup-frontend
	$(PIPENV) install --dev

test: version-file
	$(RUNNER) flake8 .
	$(RUNNER) isort --check-only -rc ./app ./tests
	$(RUNNER) py.test --cov=app --cov-report=term-missing tests/ --junitxml=test_results.xml -n4 --maxfail=10
	$(NPM) test

run-gulp:
	$(NPM) run watch

run: version-file
	$(RUNNER) flask run -p $(PORT)

run-gunicorn: version-file
	$(RUNNER) gunicorn -w $(WORKERS) -b 0.0.0.0:$(PORT) -k eventlet application

pipenv-requirements.txt: Pipfile.lock
	$(PIPENV) lock -r > $@

vendor: pipenv-requirements.txt
	$(RUNNER) pip download -d $@ -r $<

requirements.txt: pipenv-requirements.txt
	cat $< | $(RUNNER) python fixup-requirements.py > $@

native-vendor:
	mkdir -p $@

build-linux-wheels: pipenv-requirements.txt native-vendor
	cat $< | $(RUNNER) python fixup-requirements.py --ignore | docker run\
		-i --rm\
		-v $(shell pwd)/build-linux-wheels.sh:/build-linux-wheels.sh\
		quay.io/pypa/manylinux1_x86_64 bash /build-linux-wheels.sh | tar -C native-vendor -x

deploy: vendor requirements.txt
	cf zero-downtime-push $(APP) -f manifest.yml

.PHONY: test setup-frontend setup setup-dev run run-gunicorn deploy build-linux-wheels

PIPENV ?= pipenv
RUNNER ?= $(PIPENV) run

# A help target including self-documenting targets (see the awk statement)
define HELP_TEXT
Usage: make [TARGET]... [MAKEVAR1=SOMETHING]...

Available targets:
endef
export HELP_TEXT
help: ## List common commands and their usage
	@echo "notify-utils"
	@echo
	@echo "$$HELP_TEXT"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Setup virtualenv and install python dependencies
	$(PIPENV) install

install-dev: ## Setup everything in dev mode for testing
	$(PIPENV) install --dev

build:
	$(RUNNER) python setup.py sdist

tests:
	$(RUNNER) python setup.py test

ROOT_TEST_FILES = $(shell find tests/test_*.py -type f)
ROOT_TESTS = $(ROOT_TEST_FILES:tests/test_%.py=test-%)

$(ROOT_TESTS): test-%:
	$(RUNNER) pytest tests/test_$*.py

check-vulnerabilities:
	$(RUNNER) bandit -c bandit.yml -r . -x tests -l

lint:
	$(RUNNER) flake8 notifications_utils

fmt:
	$(RUNNER) autopep8 --in-place --recursive .

test: lint tests

clean:
	-rm -r cache
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info

clean-full:
	-$(MAKE) clean
	-$(PIPENV) --rm

.PHONY: help build install install-dev test lint fmt tests clean clean-full check-vulnerabilities $(ROOT_TESTS)

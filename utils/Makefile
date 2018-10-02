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

setup: ## Setup virtualenv and install python dependencies
	$(PIPENV) install

setup-dev: ## Setup everything in dev mode for testing
	$(PIPENV) install --dev

build:
	$(RUNNER) python setup.py sdist

tests:
	$(RUNNER) python setup.py test

check-vulnerabilities:
	$(RUNNER) bandit -r . -x tests -ll

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

.PHONY: help build setup setup-dev test lint fmt tests clean clean-full check-vulnerabilities

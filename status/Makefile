BUNDLE ?= bundle
RUNNER ?= $(BUNDLE) exec
CF     ?= cf
APP    ?= notify-status

.DEFAULT_GOAL := help

# A help target including self-documenting targets (see the awk statement)
define HELP_TEXT
Usage: make [TARGET]... [MAKEVAR1=SOMETHING]...

Available targets:
endef
export HELP_TEXT
help: ## List common commands and their usage
	@echo "notify-status"
	@echo
	@echo "$$HELP_TEXT"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
		{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup ruby gems
	$(BUNDLE) install

setup-dev: setup

setup-db:
	$(RUNNER) rake db:setup

migrate-db:
	$(RUNNER) rake db:migrate

test:
	$(RUNNER) rake test

run:
	$(RUNNER) rails server

build:
	$(RUNNER) rake staytus:build

deploy:
	$(CF) zero-downtime-push $(APP) -f manifest.yml

create-service-mysql:
	-$(CF) create-service mysql shared notify-mysql-status

check-vulnerabilities:
clean:


.PHONY: setup setup-dev run deploy create-service-mysql setup-db migrate-db help clean check-vulnerabilities

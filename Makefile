.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

PIP_ACCEL_CACHE ?= ${CURDIR}/cache/pip-accel

BUILD_TAG ?= notifications-utils-manual
DOCKER_BUILDER_IMAGE_NAME = govuk/notifications-utils-builder
DOCKER_CONTAINER_PREFIX = ${USER}-${BUILD_TAG}

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: venv/bin/activate ## Create virtualenv if it does not exist

venv/bin/activate:
	test -d venv || virtualenv venv

.PHONY: dependencies
dependencies: venv ## Install build dependencies
	./venv/bin/pip install pip-accel
	mkdir -p ${PIP_ACCEL_CACHE}
	PIP_ACCEL_CACHE=${PIP_ACCEL_CACHE} ./venv/bin/pip-accel install -r requirements_for_test.txt

.PHONY: build
build: dependencies ## Build project

.PHONY: test
test: venv ## Run tests
	./scripts/run_tests.sh

.PHONY: prepare-docker-build-image
prepare-docker-build-image: ## Prepare the Docker builder image
	mkdir -p ${PIP_ACCEL_CACHE}
	make -C docker build

.PHONY: build-with-docker
build-with-docker: prepare-docker-build-image ## Build inside a Docker container
	@docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-build" \
		-v `pwd`:/var/project \
		-v ${PIP_ACCEL_CACHE}:/var/project/cache/pip-accel \
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		-e NO_PROXY="${NO_PROXY}" \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make build

.PHONY: test-with-docker
test-with-docker: prepare-docker-build-image ## Run tests inside a Docker container
	@docker run -i --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-test" \
		-v `pwd`:/var/project \
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		-e NO_PROXY="${NO_PROXY}" \
		${DOCKER_BUILDER_IMAGE_NAME} \
		make test

.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true

clean:
	rm -rf cache venv

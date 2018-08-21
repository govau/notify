MAIN     = src/index.js
YARN    ?= yarn
NODE    ?= node
NODEMON ?= $(YARN) run nodemon
RUNNER  ?= $(NODE)

yarn.lock node_modules: package.json
	$(YARN)

setup: yarn.lock node_modules

run:
	$(RUNNER) $(MAIN)

dev:
	RUNNER="$(NODEMON)" $(MAKE) run

test:

clean:

.PHONY: setup start run test clean

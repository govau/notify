MAIN     = src/index.js
YARN    ?= yarn
NODE    ?= node
NODEMON ?= $(YARN) run nodemon
RUNNER  ?= $(NODE)
CF      ?= cf
APP     ?= notify-graphql-api
STG     ?= dev

build:

yarn.lock node_modules: package.json
	$(YARN)

setup: yarn.lock node_modules

run:
	$(RUNNER) $(MAIN)

dev:
	RUNNER="$(NODEMON)" $(MAKE) run

test:

clean:

manifest-vars-%.yml:
	echo "stg: $*" > $@

deploy: $(MAIN)
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: manifest-vars-$(STG).yml
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file $<

.PHONY: setup start run test clean deploy deploy-dev

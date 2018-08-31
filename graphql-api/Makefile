MAIN     = src/index.js
YARN    ?= yarn
NODE    ?= node
NODEMON ?= $(YARN) run nodemon
RUNNER  ?= $(NODE)
CF      ?= cf
APP     ?= notify-graphql-api
STG     ?= dev

PROTO_SRC   = ../proto
PROTO_DST   = proto
SCHEMAS     = notify.proto

build: $(SCHEMAS)

$(SCHEMAS:%=$(PROTO_DST)/%): $(PROTO_DST)/%: $(PROTO_SRC)/%
	@mkdir -p $(@D)
	cp $< $@

$(SCHEMAS): %: $(PROTO_DST)/%

yarn.lock node_modules: package.json
	$(YARN)

setup: yarn.lock node_modules

run:
	$(RUNNER) $(MAIN)

dev: build
	RUNNER="$(NODEMON)" $(MAKE) run

test:

clean:
	-rm -r proto
	-rm manifest-vars-*.yml

manifest-vars-%.yml:
	echo "stg: $*" > $@

deploy: $(MAIN)
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: manifest-vars-$(STG).yml
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file $<

.PHONY: setup start run test clean deploy deploy-dev

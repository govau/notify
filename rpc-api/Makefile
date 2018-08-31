PROTOC ?= protoc
GO     ?= go
CF     ?= cf
APP    ?= notify-rpc-api
STG    ?= dev
CI     ?=
DEPLOY ?= $(CI)

PROTO   = ../proto
SCHEMA  = $(PROTO)/notify.proto
SRC     = $(SCHEMA)
CMDS    = notify-rpc-api

GENERATED = notify/notify.pb.go

ifneq ($(DEPLOY),)
	export GOOS   = linux
	export GOARCH = amd64
endif

build: $(CMDS)

setup:
	@echo 'Install protoc through homebrew -- brew install protobuf'

test:
	$(GO) test ./...

$(GENERATED): $(SCHEMA)
	@mkdir -p $(@D)
	$(PROTOC) -I $(PROTO) --go_out=plugins=grpc:notify $(SCHEMA)

.SECONDEXPANSION:
$(CMDS): %: $(SRC) $(GENERATED) $$(wildcard cmd/%/*.go)
	$(GO) build ./cmd/$@


$(CMDS:%=run-%): run-%: $(SRC) $(GENERATED)
	$(GO) run cmd/$*/*.go

clean:
	-rm $(CMDS)
	-rm Procfile
	-rm manifest-vars-*.yml

run:
	$(MAKE) run-notify-rpc-api

manifest-vars-%.yml:
	echo "stg: $*" > $@

Procfile:
	echo "web: ./$(APP)" > $@

deploy: $(APP) Procfile
	$(CF) zero-downtime-push $(APP) -f manifest.yml

deploy-dev: $(APP) Procfile manifest-vars-$(STG).yml
	$(CF) push $(APP)-$(STG) -f manifest-dev.yml --vars-file manifest-vars-$(STG).yml

.PHONY: setup $(CMDS:%=run-%) run test clean

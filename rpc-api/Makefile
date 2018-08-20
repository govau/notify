PROTOC ?= protoc
GO     ?= go

PROTO   = ../proto
SCHEMA  = $(PROTO)/notify.proto
SRC     = $(SCHEMA)
CMDS    = grpc

GENERATED = notify/notify.pb.go

build: $(CMDS)

setup:
	@echo 'Install protoc through homebrew -- brew install protobuf'

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

run:
	$(MAKE) run-grpc

.PHONY: setup $(CMDS:%=run-%) run clean

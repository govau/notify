PROTOC?= protoc
GO    ?= go

PROTO  = ../proto
SCHEMA = $(PROTO)/notify.proto
SRC    = grpc.go $(SCHEMA)

GENERATED = notify/notify.pb.go

$(GENERATED): $(SCHEMA)
	@mkdir -p $(@D)
	$(PROTOC) -I $(PROTO) --go_out=plugins=grpc:notify $(SCHEMA)

setup:
	go get -u google.golang.org/grpc
	go get -u gopkg.in/square/go-jose.v2
	go get -u github.com/golang/protobuf/protoc-gen-go
	@echo 'Install protoc through homebrew -- brew install protobuf'

run: $(SRC) $(GENERATED)
	go run grpc.go

.PHONY: setup run

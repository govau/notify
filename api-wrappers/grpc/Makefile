SRC    = grpc.go defs/notify.proto
SCHEMA = defs/notify.pb.go

setup:
	go get -u google.golang.org/grpc
	go get -u gopkg.in/square/go-jose.v2
	go get -u google.golang.org/grpc
	go get -u github.com/golang/protobuf/protoc-gen-go
	@echo 'Install protoc through homebrew -- brew install protobuf'

$(SCHEMA): $(SRC)
	go generate

run: $(SCHEMA) $(SRC)
	go run grpc.go

.PHONY: setup run

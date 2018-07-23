SRC    = graphql.go schema.graphql
SCHEMA = defs/notify.pb.go

setup:
	go get -u google.golang.org/grpc
	go get -u github.com/graph-gophers/graphql-go

run:
	go run graphql.go

.PHONY: setup run

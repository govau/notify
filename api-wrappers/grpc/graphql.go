package main

import (
	"log"
	"time"

	notify "./defs"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

const (
	address = "localhost:50051"
)

func main() {
	// Set up a connection to the server.
	conn, err := grpc.Dial(address, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	c := notify.NewNotifyClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	r, err := c.GetUsers(ctx, &notify.Request{UserId: "hello. thanks"})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}

	log.Println(r)
	log.Println(err)
}

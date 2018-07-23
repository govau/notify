package main

import (
	"io/ioutil"
	"log"
	"net/http"
	"time"

	notify "./defs"
	graphql "github.com/graph-gophers/graphql-go"
	"github.com/graph-gophers/graphql-go/relay"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

const (
	address = "localhost:50051"
)

type Resolver struct {
	client notify.NotifyClient
}

type User struct {
	client notify.NotifyClient
	user   *notify.User
}

func (r *Resolver) User(ctx context.Context, args struct{ ID string }) (*User, error) {
	user, err := r.client.GetUser(ctx, &notify.ForUserRequest{UserId: args.ID})
	return &User{r.client, user}, err
}

func (r *Resolver) Users(ctx context.Context) (*[]User, error) {
	var generics []User

	users, err := r.client.GetUsers(ctx, &notify.Empty{})
	for _, user := range users.Users {
		generics = append(generics, User{r.client, user})
	}

	return &generics, err
}

func (u User) Id() *string {
	return &u.user.Id
}

func (u User) Name() *string {
	return &u.user.Name
}

func (u User) AuthType() *string {
	return &u.user.AuthType
}

func (u User) EmailAddress() *string {
	return &u.user.EmailAddress
}

func (u User) FailedLoginCount() *int32 {
	wow := int32(u.user.FailedLoginCount)
	return &wow
}

func (u User) PasswordChangedAt() *string {
	return &u.user.PasswordChangedAt
}

func (u User) Permissions() *[]Permission {
	var generics []Permission

	for service, permissions := range u.user.Permissions {
		for _, permission := range permissions.Permissions {
			generics = append(generics, Permission{service, permission})
		}
	}

	return &generics
}

type Permission struct {
	service, permission string
}

func (p Permission) Service() *string {
	return &p.service
}

func (p Permission) Permission() *string {
	return &p.permission
}

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

	r, err := c.GetUsers(ctx, &notify.Empty{})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}

	log.Println(r)
	log.Println(err)

	sfile, err := ioutil.ReadFile("schema.graphql")
	if err != nil {
		log.Fatal(err)
	}

	schema := graphql.MustParseSchema(string(sfile), &Resolver{c})
	http.Handle("/query", &relay.Handler{Schema: schema})
	http.Handle("/", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "graphiql.html")
	}))

	log.Fatal(http.ListenAndServe(":8080", nil))
}

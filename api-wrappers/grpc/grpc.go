package main

//go:generate protoc --go_out=plugins=grpc:. defs/notify.proto

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"time"

	notify "./defs"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
	jose "gopkg.in/square/go-jose.v2"
	"gopkg.in/square/go-jose.v2/jwt"
)

type Client struct {
	http.Client

	BaseURL     *url.URL
	ServiceID   string
	API_Key     string
	RouteSecret string
}

func CreateJWT(clientID, secret string) (string, error) {
	key := jose.SigningKey{Algorithm: jose.HS256, Key: []byte(secret)}
	sig, err := jose.NewSigner(key, (&jose.SignerOptions{}).WithType("JWT"))
	if err != nil {
		return "", err
	}

	cl := jwt.Claims{
		Issuer:   clientID,
		IssuedAt: jwt.NewNumericDate(time.Now()),
	}

	return jwt.Signed(sig).Claims(cl).CompactSerialize()
	return jwt.Signed(sig).Claims(cl).FullSerialize()
}

func (c Client) Do(req *http.Request) (*http.Response, error) {
	token, err := CreateJWT(c.ServiceID, c.API_Key)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Content-type", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", token))
	req.Header.Add("X-Custom-Forwarder", "")
	req.Header.Add("User-agent", "NOTIFY-API-PYTHON-CLIENT/4.9.0")

	req.URL.Host = ""
	req.URL.Scheme = ""
	req.URL = c.BaseURL.ResolveReference(req.URL)

	return c.Client.Do(req)
}

func (c Client) Get(path string) (*http.Response, error) {
	req, err := http.NewRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}

	return c.Do(req)
}

type DataJSON struct {
	Data json.RawMessage `json:"data"`
}

func JSONData(reader io.Reader) (json.RawMessage, error) {
	var buf bytes.Buffer
	_, err := io.Copy(&buf, reader)

	return buf.Bytes(), err
}

func JSONDataNested(reader io.Reader) (json.RawMessage, error) {
	var data DataJSON
	err := json.NewDecoder(reader).Decode(&data)
	return data.Data, err
}

func (c Client) Users() (json.RawMessage, error) {
	resp, err := c.Get("/user")
	if err != nil {
		return nil, err
	}

	return JSONDataNested(resp.Body)
}

type server struct {
	c Client
}

type User struct {
	Name              string              `json:"name"`
	AuthType          string              `json:"auth_type"`
	EmailAddress      string              `json:"email_address"`
	FailedLoginCount  int64               `json:"failed_login_count"`
	PasswordChangedAt string              `json:"password_changed_at"`
	Permissions       map[string][]string `json:"permissions"`
}

type Users []User

func (u Users) Protoify() *notify.Users {
	users := [](*notify.User){}

	for _, user := range u {
		permissions := map[string]*notify.Permissions{}

		for service, ps := range user.Permissions {
			permissions[service] = &notify.Permissions{Permissions: ps}
		}

		users = append(users, &notify.User{
			Name:              user.Name,
			AuthType:          user.AuthType,
			EmailAddress:      user.EmailAddress,
			FailedLoginCount:  user.FailedLoginCount,
			PasswordChangedAt: user.PasswordChangedAt,
			Permissions:       permissions,
		})
	}

	return &notify.Users{Users: users}
}

func (s *server) GetUsers(ctx context.Context, in *notify.Request) (*notify.Users, error) {
	log.Println("Getting users")
	log.Println(in.UserId)

	usersJSON, err := s.c.Users()
	if err != nil {
		return nil, err
	}

	var users Users
	err = json.Unmarshal(usersJSON, &users)
	return users.Protoify(), err
}

func main() {
	baseURL, err := url.Parse("http://localhost:6011")
	if err != nil {
		log.Fatal(err)
	}

	c := Client{
		BaseURL:     baseURL,
		ServiceID:   "notify-admin",
		API_Key:     "dev-notify-secret-key",
		RouteSecret: "",
	}

	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	notify.RegisterNotifyServer(s, &server{c})
	reflection.Register(s)

	go log.Println("going out to listen now!")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

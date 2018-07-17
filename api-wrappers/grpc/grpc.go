package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"

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

func (c Client) Users() (json.RawMessage, error) {
	var buf bytes.Buffer
	resp, err := c.Get("/user")
	if err != nil {
		return nil, err
	}

	_, err = io.Copy(&buf, resp.Body)
	return buf.Bytes(), err
}

func main() {
	fmt.Println("vim-go")

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

	log.Println(CreateJWT(c.ServiceID, c.API_Key))

	users, err := c.Users()
	if err != nil {
		log.Fatal(err)
	}
	log.Println(string(users))
}

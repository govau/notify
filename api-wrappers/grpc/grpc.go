package main

//go:generate protoc --go_out=plugins=grpc:. defs/notify.proto

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
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

func (c Client) Services(userID string) (json.RawMessage, error) {
	resp, err := c.Get(fmt.Sprintf("/service?user_id=%s", userID))
	if err != nil {
		return nil, err
	}

	return JSONDataNested(resp.Body)
}

func (c Client) Templates(serviceID string) (json.RawMessage, error) {
	resp, err := c.Get(fmt.Sprintf("/service/%s/template", serviceID))
	if err != nil {
		return nil, err
	}

	return JSONDataNested(resp.Body)
}

type server struct {
	c Client
}

type Service struct {
	Active           bool     `json:"active"`
	Branding         string   `json:"branding"`
	CreatedBy        string   `json:"created_by"`
	EmailFrom        string   `json:"email_from"`
	Id               string   `json:"id"`
	Name             string   `json:"name"`
	OrganisationType string   `json:"organisation_type"`
	RateLimit        int64    `json:"rate_limit"`
	AnnualBilling    []string `json:"annual_billing"`
	Permissions      []string `json:"permissions"`
	UserToService    []string `json:"user_to_service"`
	Users            []string `json:"users"`
}

type Services []Service

func (s Services) Protoify() *notify.Services {
	services := [](*notify.Service){}

	for _, service := range s {
		services = append(services, &notify.Service{
			Active:           service.Active,
			Branding:         service.Branding,
			CreatedBy:        service.CreatedBy,
			EmailFrom:        service.EmailFrom,
			Id:               service.Id,
			Name:             service.Name,
			OrganisationType: service.OrganisationType,
			RateLimit:        service.RateLimit,
			AnnualBilling:    service.AnnualBilling,
			UserToService:    service.UserToService,
			Permissions:      service.Permissions,
			Users:            service.Users,
		})
	}

	return &notify.Services{Services: services}
}

type Template struct {
	Id           string `json:"id"`
	Name         string `json:"name"`
	Subject      string `json:"subject"`
	Content      string `json:"content"`
	TemplateType string `json:"template_type"`
	CreatedAt    string `json:"created_at"`
	CreatedBy    string `json:"created_by"`
	Service      string `json:"service"`
	ProcessType  string `json:"process_type"`
	Archived     bool   `json:"archived"`
}

type Templates []Template

func (t Templates) Protoify() *notify.Templates {
	templates := [](*notify.Template){}

	for _, template := range t {
		templates = append(templates, &notify.Template{
			Id:           template.Id,
			Name:         template.Name,
			Subject:      template.Subject,
			Content:      template.Content,
			TemplateType: template.TemplateType,
			CreatedAt:    template.CreatedAt,
			CreatedBy:    template.CreatedBy,
			Service:      template.Service,
			ProcessType:  template.ProcessType,
			Archived:     template.Archived,
		})
	}

	return &notify.Templates{Templates: templates}
}

type User struct {
	Id                string              `json:"id"`
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
			Id:                user.Id,
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

	if in.UserId == "FAIL_NOW" {
		return nil, errors.New("failing because you said the magic word")
	}

	usersJSON, err := s.c.Users()
	if err != nil {
		return nil, err
	}

	var users Users
	err = json.Unmarshal(usersJSON, &users)
	return users.Protoify(), err
}

func (s *server) ServicesForUser(ctx context.Context, in *notify.ServiceRequest) (*notify.Services, error) {
	log.Println("Getting services")
	log.Println(in.UserId)

	servicesJSON, err := s.c.Services(in.UserId)
	if err != nil {
		return nil, err
	}

	var services Services
	err = json.Unmarshal(servicesJSON, &services)
	return services.Protoify(), err
}

func (s *server) TemplatesForService(ctx context.Context, in *notify.TemplatesRequest) (*notify.Templates, error) {
	log.Println("Getting templates")
	log.Println(in.ServiceId)

	templatesJSON, err := s.c.Templates(in.ServiceId)
	if err != nil {
		return nil, err
	}

	var templates Templates
	err = json.Unmarshal(templatesJSON, &templates)
	return templates.Protoify(), err
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

package cmd

import (
	"bytes"
	"encoding/json"
	"errors"
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

	resp, err := c.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 300 {
		return resp, fmt.Errorf("bad status code %d", resp.StatusCode)
	}

	return resp, nil
}

func (c Client) Post(path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest("POST", path, body)
	if err != nil {
		return nil, err
	}

	resp, err := c.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode > 300 {
		defer resp.Body.Close()
		var buf bytes.Buffer
		io.Copy(&buf, resp.Body)

		log.Println("failed request", buf.String())
		return resp, errors.New("bad status code")
	}

	return resp, nil
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

func (c Client) Users() (Users, error) {
	var v Users

	resp, err := c.Get("/user")
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err

}

func (c Client) User(userID string) (User, error) {
	var v User

	resp, err := c.Get(fmt.Sprintf("/user/%s", userID))
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err
}

func (c Client) Service(serviceID string) (Service, error) {
	var v Service

	resp, err := c.Get(fmt.Sprintf("/service/%s", serviceID))
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err
}

func (c Client) Services(userID string) (Services, error) {
	var v Services

	resp, err := c.Get(fmt.Sprintf("/service?user_id=%s", userID))
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err
}

func (c Client) CreateTemplate(serviceID string, template Template) (Template, error) {
	var v Template

	var buf bytes.Buffer
	err := json.NewEncoder(&buf).Encode(template)
	if err != nil {
		return v, err
	}

	resp, err := c.Post(
		fmt.Sprintf("/service/%s/template", serviceID),
		&buf,
	)
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err

}

func (c Client) Templates(serviceID string) (Templates, error) {
	var v Templates

	resp, err := c.Get(fmt.Sprintf("/service/%s/template", serviceID))
	if err != nil {
		return v, err
	}
	defer resp.Body.Close()

	j, err := JSONDataNested(resp.Body)
	if err != nil {
		return v, err
	}

	err = json.Unmarshal(j, &v)
	return v, err
}

type Service struct {
	Active           bool     `json:"active" gqlgen:"active"`
	Branding         string   `json:"branding" gqlgen:"branding"`
	CreatedByID      string   `json:"created_by"`
	EmailFrom        string   `json:"email_from" gqlgen:"email_from"`
	Id               string   `json:"id" gqlgen:"id"`
	Name             string   `json:"name" gqlgen:"name"`
	OrganisationType string   `json:"organisation_type" gqlgen:"organisation_type"`
	RateLimit        int      `json:"rate_limit" gqlgen:"rate_limit"`
	AnnualBilling    []string `json:"annual_billing"`
	Permissions      []string `json:"permissions" gqlgen:"permissions"`
	UserToService    []string `json:"user_to_service"`
	Users            []string `json:"users"`
}

type Services []Service

type Template struct {
	Id           string `json:"id,omitempty" json:"gqlgen,omitempty"`
	Name         string `json:"name" gqlgen:"name"`
	Subject      string `json:"subject" gqlgen:"subject"`
	Content      string `json:"content" gqlgen:"content"`
	TemplateType string `json:"template_type" gqlgen:"template_type"`
	CreatedAt    string `json:"created_at" gqlgen:"created_at"`
	CreatedBy    string `json:"created_by" gqlgen:"created_by"`
	ServiceID    string `json:"service"`
	ProcessType  string `json:"process_type" gqlgen:"process_type"`
	Archived     bool   `json:"archived" gqlgen:"archived"`
}

type Templates []Template

type User struct {
	Id                string              `json:"id" gqlgen:"id"`
	Name              string              `json:"name" gqlgen:"name"`
	AuthType          string              `json:"auth_type" gqlgen:"auth_type"`
	EmailAddress      string              `json:"email_address" gqlgen:"email_address"`
	FailedLoginCount  int                 `json:"failed_login_count" gqlgen:"failed_login_count"`
	PasswordChangedAt string              `json:"password_changed_at" gqlgen:"password_changed_at"`
	PermissionsMap    map[string][]string `json:"permissions"`
}

type Permission struct {
	Service    string
	Permission string
}

type Users []User

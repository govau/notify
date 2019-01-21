package rpc_api

import (
	"context"
	"net/url"

	"github.com/govau/notify/rpc-api/cmd"
)

var base, _ = url.Parse("http://localhost:6011")

var c = cmd.Client{
	BaseURL:     base,
	ServiceID:   "notify-admin",
	API_Key:     "dev-notify-secret-key",
	RouteSecret: "",
}

type Resolver struct{}

func (r *Resolver) Mutation() MutationResolver {
	return &mutationResolver{r}
}
func (r *Resolver) Query() QueryResolver {
	return &queryResolver{r}
}
func (r *Resolver) Service() ServiceResolver {
	return &serviceResolver{r}
}
func (r *Resolver) Template() TemplateResolver {
	return &templateResolver{r}
}
func (r *Resolver) User() UserResolver {
	return &userResolver{r}
}

type mutationResolver struct{ *Resolver }

func (r *mutationResolver) CreateTemplate(ctx context.Context, service_id string, created_by string, name string, subject string, content string) (*cmd.Template, error) {
	panic("not implemented")
}

type queryResolver struct{ *Resolver }

func (r *queryResolver) User(ctx context.Context, id string) (*cmd.User, error) {
	panic("not implemented")
}
func (r *queryResolver) Users(ctx context.Context) ([]cmd.User, error) {
	return c.Users()
}

type serviceResolver struct{ *Resolver }

func (r *serviceResolver) Templates(ctx context.Context, obj *cmd.Service) ([]cmd.Template, error) {
	return c.Templates(obj.Id)
}
func (r *serviceResolver) CreatedBy(ctx context.Context, obj *cmd.Service) (*cmd.User, error) {
	user, err := c.User(obj.CreatedByID)
	return &user, err
}

type templateResolver struct{ *Resolver }

func (r *templateResolver) Service(ctx context.Context, obj *cmd.Template) (*cmd.Service, error) {
	service, err := c.Service(obj.ServiceID)
	return &service, err
}

type userResolver struct{ *Resolver }

func (r *userResolver) Permissions(ctx context.Context, obj *cmd.User) ([]cmd.Permission, error) {
	panic("not implemented")
}
func (r *userResolver) Services(ctx context.Context, obj *cmd.User) ([]cmd.Service, error) {
	return c.Services(obj.Id)
}

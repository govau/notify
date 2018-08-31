PIPENV      ?= pipenv
RUNNER      ?= $(PIPENV) run
CF          ?= cf
CF_SPACE_ID ?= f2c9cbdc-9449-4da9-8825-899e3142f783
GIT_REMOTE  ?= https://github.com/govau/notify

list-branches:
	git ls-remote --heads ${GIT_REMOTE} | egrep "/feat-.*" | $(RUNNER) python remove_feat_prefix.py

list-apps:
	$(CF) curl "/v2/spaces/${CF_SPACE_ID}/apps" | jq -r ".resources[].entity.name"

list-services:
	$(CF) curl "/v2/spaces/${CF_SPACE_ID}/service_instances" | jq -r ".resources[].entity.name"

undeploy-feature-branches:
	$(RUNNER) python undeploy_closed_branches.py

undeploy-%:
	-$(CF) unbind-service notify-api-f-$* notify-psql-f-$*
	-$(CF) unbind-service notify-celery-f-$* notify-psql-f-$*
	-$(CF) delete notify-f-$* -f
	-$(CF) delete notify-api-f-$* -f
	-$(CF) delete notify-celery-f-$* -f
	-$(CF) delete notify-rpc-api-f-$* -f
	-$(CF) delete notify-graphql-api-f-$* -f
	-$(CF) delete-service notify-psql-f-$* -f

.PHONY: list-branches list-apps list-services list-deployed-features prune

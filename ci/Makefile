CF_SPACE_ID   ?= f2c9cbdc-9449-4da9-8825-899e3142f783
GIT_REMOTE    ?= https://github.com/govau/notify
PIPENV        ?= pipenv
RUNNER        ?= $(PIPENV) run
CF            ?= cf
AWS           ?= aws
JQ            ?= jq
DIFF          ?= diff

CLD_Y         ?= y.cld.gov.au
CLD_B         ?= b.cld.gov.au
CLD_HOST      ?= $(CLD_Y)
STG           ?= dev

SERVICES       = notify-shared notify-api notify-admin notify-celery aws smtp telstra twilio
SVC_APPLIED    = $(SERVICES:%=apply-service-%)
SVC_CREATED    = $(SERVICES:%=create-service-%)
SVC_DIFFED     = $(SERVICES:%=diff-service-%)
SVC_FETCHED    = $(SERVICES:%=fetch-service-%)
APPLY_ACTION  ?= update

PSQL_SVC_PLAN ?= shared
PSQL_SVC_NAME ?= notify-psql-$(STG)


apply-services: $(SVC_APPLIED)

fetch-services: $(SVC_FETCHED)

diff-services: $(SVC_DIFFED)

ups/$(CLD_HOST)/%.json:
	-mkdir -p $(@D)
	$(CF) curl "/v2/user_provided_service_instances?q=name:$*" | $(JQ) -S ".resources[].entity.credentials" > $@

$(SVC_APPLIED): apply-service-%: ups/$(CLD_HOST)/%.json
	$(CF) $(APPLY_ACTION)-user-provided-service $* -p $<

$(SVC_CREATED): create-service-%:
	$(MAKE) apply-service-$* APPLY_ACTION=create

$(SVC_DIFFED): SHELL = /bin/bash
$(SVC_DIFFED): diff-service-%:
	@$(DIFF) \
	  <($(CF) curl "/v2/user_provided_service_instances?q=name:$*" | $(JQ) -S ".resources[].entity.credentials") \
	  <($(JQ) -S . ups/$(CLD_HOST)/$*.json)

$(SVC_FETCHED): fetch-service-%:
	-mkdir -p ups/$(CLD_HOST)
	$(CF) curl "/v2/user_provided_service_instances?q=name:$*" | $(JQ) -S ".resources[].entity.credentials" > ups/$(CLD_HOST)/$*.json

create-service-psql:
	-$(CF) create-service postgres $(PSQL_SVC_PLAN) $(PSQL_SVC_NAME)

setup-ses-callback: export AWS_ACCESS_KEY_ID = $(SES_CALLBACK_AWS_ACCESS_KEY_ID)
setup-ses-callback: export AWS_SECRET_ACCESS_KEY = $(SES_CALLBACK_AWS_SECRET_ACCESS_KEY)
setup-ses-callback: export AWS_REGION = $(SES_CALLBACK_AWS_REGION)
setup-ses-callback: export TOPIC_ARN = $(SES_CALLBACK_AWS_SNS_TOPIC_ARN)
setup-ses-callback:
	@$(AWS) sns subscribe \
		--region $(AWS_REGION) \
		--topic-arn "$(TOPIC_ARN)" \
		--protocol https \
		--notification-endpoint "https://notify-api-$(STG).apps.y.cld.gov.au/notifications/email/ses"

teardown-ses-callback-%: export AWS_ACCESS_KEY_ID = $(SES_CALLBACK_AWS_ACCESS_KEY_ID)
teardown-ses-callback-%: export AWS_SECRET_ACCESS_KEY = $(SES_CALLBACK_AWS_SECRET_ACCESS_KEY)
teardown-ses-callback-%: export AWS_REGION = $(SES_CALLBACK_AWS_REGION)
teardown-ses-callback-%: export TOPIC_ARN = $(SES_CALLBACK_AWS_SNS_TOPIC_ARN)
teardown-ses-callback-%:
	@SUB_ARN=`$(AWS) sns list-subscriptions-by-topic \
		--region $(AWS_REGION) \
		--topic-arn "$(TOPIC_ARN)" \
		| $(JQ) -r '.Subscriptions[] | select(.Endpoint == "https://notify-api-f-$*.apps.y.cld.gov.au/notifications/email/ses").SubscriptionArn'`; \

	$(AWS) sns unsubscribe \
		--region $(AWS_REGION) \
		--subscription-arn "$$SUB_ARN"

list-branches:
	git ls-remote --heads ${GIT_REMOTE} | egrep "/feat-.*" | $(RUNNER) python remove_feat_prefix.py

list-apps:
	$(CF) curl "/v2/spaces/${CF_SPACE_ID}/apps" | $(JQ) -r ".resources[].entity.name"

list-services:
	$(CF) curl "/v2/spaces/${CF_SPACE_ID}/service_instances" | $(JQ) -r ".resources[].entity.name"

undeploy-feature-branches:
	$(RUNNER) python undeploy_closed_branches.py

undeploy-%:
	-$(CF) unbind-service notify-api-f-$* notify-psql-f-$*
	-$(CF) unbind-service notify-celery-f-$* notify-psql-f-$* # TODO: can remove once all such applications are cleaned up
	-$(CF) unbind-service notify-celery-worker-f-$* notify-psql-f-$*
	-$(CF) unbind-service notify-celery-beat-f-$* notify-psql-f-$*
	-$(CF) delete notify-f-$* -f
	-$(CF) delete notify-api-f-$* -f
	-$(CF) delete notify-celery-f-$* -f # TODO: can remove once all such applications are cleaned up
	-$(CF) delete notify-celery-worker-f-$* -f
	-$(CF) delete notify-celery-beat-f-$* -f
	-$(CF) delete notify-docs-f-$* -f
	-$(CF) delete-service notify-psql-f-$* -f

	-$(MAKE) teardown-ses-callback-$*

.PHONY: prune \
	list-branches list-apps \
	list-services list-deployed-features \
	create-service-psql \
	setup-ses-callback \
	$(SVC_APPLIED) $(SVC_CREATED) $(SVC_DIFFED) $(SVC_FETCHED)

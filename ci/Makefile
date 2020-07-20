CF_SPACE_ID   ?= 9016f67f-0bb2-48e7-aad9-00d9b755ee61
GIT_REMOTE    ?= https://github.com/govau/notify
PIPENV        ?= pipenv
RUNNER        ?= $(PIPENV) run
CF            ?= cf
AWS           ?= aws
JQ            ?= jq
DIFF          ?= diff

CLD_Y         ?= y.cld.gov.au
CLD_HOST      ?= $(CLD_Y)
STG           ?= development

SERVICES       = notify-shared notify-api notify-admin notify-celery aws smtp sap sap-covid telstra twilio
SVC_APPLIED    = $(SERVICES:%=apply-service-%)
SVC_CREATED    = $(SERVICES:%=create-service-%)
SVC_DIFFED     = $(SERVICES:%=diff-service-%)
SVC_FETCHED    = $(SERVICES:%=fetch-service-%)
APPLY_ACTION  ?= update

PSQL_SVC_PLAN ?= dev-small
PSQL_SVC_NAME ?= notify-psql-$(STG)

REDIS_SVC_PLAN ?= production
REDIS_SVC_NAME ?= notify-redis-$(STG)


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
	-$(CF) create-service postgresql $(PSQL_SVC_PLAN) $(PSQL_SVC_NAME)
	./bin/cf-wait-for-service $(PSQL_SVC_NAME)

create-service-redis:
	-$(CF) create-service redis $(REDIS_SVC_PLAN) $(REDIS_SVC_NAME)
	./bin/cf-wait-for-service $(REDIS_SVC_NAME)

setup-ses-callback: export AWS_ACCESS_KEY_ID ?= $(SES_CALLBACK_AWS_ACCESS_KEY_ID)
setup-ses-callback: export AWS_SECRET_ACCESS_KEY ?= $(SES_CALLBACK_AWS_SECRET_ACCESS_KEY)
setup-ses-callback: export AWS_REGION ?= $(SES_CALLBACK_AWS_REGION)
setup-ses-callback: export TOPIC_ARN ?= $(SES_CALLBACK_AWS_SNS_TOPIC_ARN)
setup-ses-callback: export ENDPOINT ?= "https://notify-api-$(STG).apps.y.cld.gov.au/notifications/email/ses"
setup-ses-callback:
	@$(AWS) sns subscribe \
		--region $(AWS_REGION) \
		--topic-arn "$(TOPIC_ARN)" \
		--protocol https \
		--notification-endpoint $(ENDPOINT) > /dev/null

teardown-ses-callback-%: export AWS_ACCESS_KEY_ID ?= $(SES_CALLBACK_AWS_ACCESS_KEY_ID)
teardown-ses-callback-%: export AWS_SECRET_ACCESS_KEY ?= $(SES_CALLBACK_AWS_SECRET_ACCESS_KEY)
teardown-ses-callback-%: export AWS_REGION ?= $(SES_CALLBACK_AWS_REGION)
teardown-ses-callback-%: export TOPIC_ARN ?= $(SES_CALLBACK_AWS_SNS_TOPIC_ARN)
teardown-ses-callback-%:
	$(AWS) sns unsubscribe \
		--region $(AWS_REGION) \
		--subscription-arn `$(AWS) sns list-subscriptions-by-topic \
			--region $(AWS_REGION) \
			--topic-arn "$(TOPIC_ARN)" \
			| $(JQ) -r '.Subscriptions[] | select(.Endpoint == "https://notify-api-$*.apps.y.cld.gov.au/notifications/email/ses").SubscriptionArn'`

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
	-$(CF) unbind-service notify-api-f-$* notify-redis-f-$*
	-$(CF) delete notify-f-$* -f
	-$(CF) delete notify-api-f-$* -f
	-$(CF) delete notify-celery-worker-f-$* -f # TODO: remove once all cleaned up
	-$(CF) delete notify-celery-worker-default-f-$* -f
	-$(CF) delete notify-celery-worker-priority-f-$* -f
	-$(CF) delete notify-celery-worker-sender-f-$* -f
	-$(CF) delete notify-celery-worker-callbacks-f-$* -f
	-$(CF) delete notify-celery-worker-retrys-f-$* -f
	-$(CF) delete notify-celery-worker-internal-f-$* -f
	-$(CF) delete notify-celery-beat-f-$* -f
	-$(CF) delete notify-docs-f-$* -f
	-$(CF) delete-service notify-psql-f-$* -f
	-$(CF) delete-service notify-redis-f-$* -f

	-$(MAKE) teardown-ses-callback-f-$*

LOADTESTING_CMDS = run

$(LOADTESTING_CMDS:%=loadtesting-%): loadtesting-%:
	$(MAKE) -C loadtesting $*

.PHONY: prune \
	list-branches list-apps \
	list-services list-deployed-features \
	create-service-psql \
	create-service-redis \
	setup-ses-callback \
	$(LOADTESTING_CMDS:%=loadtesting-%) \
	$(SVC_APPLIED) $(SVC_CREATED) $(SVC_DIFFED) $(SVC_FETCHED)

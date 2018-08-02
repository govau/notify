CLD_Y       ?= y.cld.gov.au
CLD_B       ?= b.cld.gov.au
CLD_HOST    ?= $(CLD_Y)
CF_API      ?= https://api.system.$(CLD_HOST)
CF_ORG      ?= dta
CF_SPACE    ?= notifications
CF_HOME     ?= $(HOME)
CF          ?= cf

TARGETS      = setup deploy
SERVICES     = notify-shared notify-api notify-admin aws smtp telstra
SVC_APPLIED  = $(SERVICES:%=apply-service-%)
SVC_CREATED  = $(SERVICES:%=create-service-%)
APPLY_ACTION?= update

PSQL_SVC_NAME ?= notify-psql
PSQL_SVC_PLAN ?= shared

all: setup

# this is a hack because CircleCI env variables are awful
CF_USERNAME ?= $(CF_Y_USER)
CF_PASSWORD ?= $(CF_Y_PASSWORD)

cf-login:
	@$(CF) login\
		-a "${CF_API}"\
		-u "${CF_USERNAME}"\
		-p "${CF_PASSWORD}"\
		-o "${CF_ORG}"\
		-s "${CF_SPACE}"

cf-login-prod:
	@$(MAKE)\
	  CF_USERNAME=${CF_B_USER}\
	  CF_PASSWORD=${CF_B_PASSWORD}\
	  CLD_HOST=${CLD_B}\
	  CF_SPACE=notify\
	  cf-login

$(TARGETS):
	$(MAKE) -C api $@
	$(MAKE) -C admin $@

apply-services: $(SVC_APPLIED)

$(SVC_APPLIED): apply-service-%: ci/ups/$(CLD_HOST)/%.json
	$(CF) $(APPLY_ACTION)-user-provided-service $* -p $<

$(SVC_CREATED): create-service-%:
	$(MAKE) apply-service-$* APPLY_ACTION=create

create-service-psql:
	$(CF) create-service postgres $(PSQL_SVC_PLAN) $(PSQL_SVC_NAME)

.PHONY: cf-login $(TARGETS) $(SVC_APPLIED) $(SVC_CREATED) create-service-psql

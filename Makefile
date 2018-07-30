CLD_HOST    ?= y.cld.gov.au
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

all: setup

cf-login:
	@$(CF) login\
		-a "${CF_API}"\
		-u "${CF_USERNAME}"\
		-p "${CF_PASSWORD}"\
		-o "${CF_ORG}"\
		-s "${CF_SPACE}"

$(TARGETS):
	$(MAKE) -C api $@
	$(MAKE) -C admin $@

apply-services: $(SVC_APPLIED)

$(SVC_APPLIED): apply-service-%: ci/ups/$(CLD_HOST)/%.json
	$(CF) $(APPLY_ACTION)-user-provided-service $* -p $<

$(SVC_CREATED): create-service-%:
	$(MAKE) apply-service-$* APPLY_ACTION=create

.PHONY: cf-login $(TARGETS) $(SVC_APPLIED) $(SVC_CREATED)

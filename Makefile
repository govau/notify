CLD_HOST   ?= y.cld.gov.au
DEPLOY_ENV ?= notifications
CF_API     ?= https://api.system.$(CLD_HOST)
CF_ORG     ?= dta
CF_SPACE   ?= $(DEPLOY_ENV)
CF_HOME    ?= $(HOME)

TARGETS    = setup deploy

all: setup

cf-login:
	@cf login\
		-a "${CF_API}"\
		-u "${CF_USERNAME}"\
		-p "${CF_PASSWORD}"\
		-o "${CF_ORG}"\
		-s "${CF_SPACE}"

$(TARGETS):
	$(MAKE) -C api $@
	$(MAKE) -C admin $@

.PHONY: cf-login setup deploy

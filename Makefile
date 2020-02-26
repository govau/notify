CLD_Y       ?= y.cld.gov.au
CLD_B       ?= b.cld.gov.au
CLD_HOST    ?= $(CLD_Y)
CF_API      ?= https://api.system.$(CLD_HOST)
CF_ORG      ?= dta
CF_SPACE    ?= notifications
CF_HOME     ?= $(HOME)
CF          ?= cf

# deploys can respond to STG env variable if they support
# feature branches or alternate production builds
PRD_BRANCH    ?= master
PRD_STAGE     ?= stg
STG_PREFIX    ?= feat-
CIRCLE_BRANCH ?=
BRANCH        ?= $(CIRCLE_BRANCH)
FEATURE        = $(BRANCH:$(STG_PREFIX)%=%)

# set prod stage if we're on prod branch
ifeq ($(BRANCH), $(PRD_BRANCH))
	export STG ?= $(PRD_STAGE)
endif

# export stg variable only if we are on a feature branch
ifneq ($(BRANCH), $(FEATURE))
	export STG ?= f-$(FEATURE)
endif

all: install

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

DIRS        = api admin utils status docs
TARGETS     = install install-dev build check-vulnerabilities clean deploy deploy-dev test
API_TARGETS = run-celery-worker-sender run-celery-worker run-celery-beat deploy-celery-worker-sender deploy-celery-worker deploy-dev-celery-worker-sender deploy-dev-celery-worker deploy-celery-beat deploy-dev-celery-beat
CI_TARGETS  = create-service-psql setup-ses-callback setup-sqs-queues
ANY_TARGETS = $(TARGETS) $(API_TARGETS) $(CI_TARGETS)

$(ANY_TARGETS:%=\%.%):
	$(MAKE) -C $* $(@:$*.%=%)

$(TARGETS):
	$(MAKE) $(DIRS:%=%.$@)

$(API_TARGETS):
	$(MAKE) api.$@

$(CI_TARGETS):
	$(MAKE) ci.$@

.PHONY: cf-login cf-login-prod $(TARGETS) $(API_TARGETS) $(CI_TARGETS)

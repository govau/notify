CF_HOME ?= $(HOME)
CF      ?= cf

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

cf-login:
	$(CF) login\
		-a "https://api.system.y.cld.gov.au"\
		-u "${CF_USERNAME}"\
		-p "${CF_PASSWORD_STAGING}"\
		-o "dta_notify"\
		-s "notify"

cf-login-prod:
	@$(CF) login\
		-a "https://api.system.b.cld.gov.au"\
		-u "${CF_B_USER}"\
		-p "${CF_B_PASSWORD}"\
		-o "dta"\
		-s "notify"

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

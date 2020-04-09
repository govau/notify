K6          ?= k6
CONCURRENCY ?= 32
DURATION    ?= 1m
RUN_SCRIPT  ?= runner.js

run: $(RUN_SCRIPT)
	$(K6) run -u $(CONCURRENCY) -d $(DURATION) --out cloud $(RUN_SCRIPT)

.PHONY: run

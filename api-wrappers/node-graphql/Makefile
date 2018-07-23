SRC    = src/index.js src/grpc.js
YARN  ?= yarn
NODE  ?= node

setup:
	$(YARN)

start:
	ls $(SRC) | entr -rc $(MAKE) run

run:
	$(NODE) src/index.js

.PHONY: setup start run

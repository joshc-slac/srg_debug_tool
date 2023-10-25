SHELL:=/bin/bash
VERSION=0x03

.PHONY: setup
setup:
	@if [ -e "bin/activate" ]; then \
		echo "venv already configured"; \
	else \
		@python3 -m venv . ; \
	fi

.PHONY: run
run:
	python3 SRGTester.py

.PHONY: request_reading
request_reading:
	@python3 testClient.py -m PERFORM_READING
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
	@python3 main.py

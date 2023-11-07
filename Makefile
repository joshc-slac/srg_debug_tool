SHELL:=/bin/bash
VERSION=0x03

FTPUSER ?=joshc

.PHONY: setup
setup:
	@if [ -e "bin/activate" ]; then \
		echo "venv already configured"; \
	else \
		@python3 -m venv . ; \
	fi
	@mkdir temp succ fail

.PHONY: run
run:
	python3 SRGTester.py

.PHONY: request_reading
request_reading:
	@source bin/activate && python3 testClient.py -m 0

.PHONY: transfer_working_files
transfer_working_files:
	rsync -zvaP --files-from=rsync-file-list . $(FTPUSER)@psbuild-rhel7:~/srg_failure_tester

.PHONY: flake8
flake8:
	@python3 -m flake8 || true

.PHONY: test
test:
	@source bin/activate && pytest tests/Test*.py
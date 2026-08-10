.PHONY: test fixtures verify-run compile security check

PYTHON ?= python3
PYTHONPYCACHEPREFIX ?= /tmp/voltstream-pycache

test:
	PYTHONPATH=src PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) -m unittest discover -s tests -v

fixtures:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) scripts/validate_fixtures.py

verify-run:
	PYTHONPATH=src PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) scripts/verify_run.py --run-id 2026-08-09-final-v4

compile:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) -m compileall -q src tests scripts

security:
	$(PYTHON) scripts/scan_secrets.py

check: test fixtures verify-run compile security

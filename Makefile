.PHONY: test fixtures compile security check

PYTHON ?= python3
PYTHONPYCACHEPREFIX ?= /tmp/voltstream-pycache

test:
	PYTHONPATH=src PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) -m unittest discover -s tests -v

fixtures:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) scripts/validate_fixtures.py

compile:
	PYTHONPYCACHEPREFIX=$(PYTHONPYCACHEPREFIX) $(PYTHON) -m compileall -q src tests scripts

security:
	$(PYTHON) scripts/scan_secrets.py

check: test fixtures compile security


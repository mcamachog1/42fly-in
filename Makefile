.PHONY: install run debug clean lint lint-strict

VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m src.engine.main

debug:
	$(PYTHON) -m pdb -m src.engine.main

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@find . -name ".mypy_cache" -type d -exec rm -rf {} +	
	
lint:
	@clear
	$(PYTHON) -m flake8 --exclude=.venv,venv,build,dist,__pycache__ .
	$(PYTHON) -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	@clear
	flake8 --exclude=.venv,venv,build,dist,__pycache__ .
	$(PYTHON) -m mypy . --strict

.PHONY: clean files install unit_tests activate

VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

unit_tests:
#	$(PYTHON) -m tests.test_load_model
	$(PYTHON) -m tests.test_enum

fly:
	$(PYTHON) -m src.engine.main
    
clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} +

files:
	@find . \( -path "./venv" -o -name ".?*" \) -prune -o -print

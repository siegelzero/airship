SHELL := /bin/bash
VENV ?= env
BIN_DIR ?= $(VENV)/bin/

# Tools
PIP ?= $(BIN_DIR)pip
PYTHON ?= $(BIN_DIR)python
PYTHON_VER := python3.7

venv:
	virtualenv $(VENV) --no-pip --python $(PYTHON_VER)
	$(BIN_DIR)easy_install pip
	$(BIN_DIR)pip install --upgrade --requirement requirements.txt

start:
	$(PYTHON) api.py

test:
	$(PYTHON) tests.py

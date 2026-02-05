# Makefile for python-experiments
# Minimal, explicit, and safe for beginners

VENV ?= .venv
PY ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip

.PHONY: help venv install run run-all clean clean-venv

help:
	@echo "Available targets:"
	@echo "  make venv          - create virtualenv in $(VENV)"
	@echo "  make install       - install runtime deps into venv"
	@echo "  make run ARGS=...  - run k8s-pods script (pass ARGS)"
	@echo "  make run-all       - run with -A (all namespaces)"
	@echo "  make clean-venv    - remove venv (destructive)"
	@echo "  make clean         - remove pyc and __pycache__"

venv:
	@python -m venv $(VENV) >/dev/null 2>&1 || true
	@echo "Created venv at $(VENV)"

install: venv
	@$(PY) -m pip install -U pip setuptools >/dev/null 2>&1 || true
	@$(PIP) install -q -r k8s-pods/requirements.txt >/dev/null 2>&1 || true
	@echo "Dependencies installed."

run:
	@if [ -x "$(PY)" ]; then \
		$(PY) k8s-pods/list-k8s-pods.py $(ARGS); \
	else \
		echo "No venv found. Run 'make install' first or run the script directly with your Python."; exit 1; \
	fi

run-all:
	@$(MAKE) run ARGS="-A $(ARGS)"

clean-venv:
	rm -rf $(VENV)

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + || true
	find . -name "*.pyc" -type f -delete || true

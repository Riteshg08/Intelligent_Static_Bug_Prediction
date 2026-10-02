.PHONY: setup test lint train

setup:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff check .

train:
	@echo "Train command not implemented yet"

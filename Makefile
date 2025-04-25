format:
	uv run -- ruff format
	uv run -- ruff check --fix

lint:
	uv run -- ruff check
	uv run -- mypy sharelatex_versioning

test:
	uv run -- pytest

all: format lint test

.PHONY: format lint test all

.DEFAULT_GOAL := all

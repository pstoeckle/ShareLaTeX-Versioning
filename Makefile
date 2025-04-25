sync:
	uv sync

format: sync
	uv run -- ruff format
	uv run -- ruff check --fix

lint: sync
	uv run -- ruff check
	uv run -- mypy sharelatex_versioning

test: sync
	uv run -- pytest

all: format lint test

.PHONY: format lint test all

.DEFAULT_GOAL := all

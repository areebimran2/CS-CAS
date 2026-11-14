# Everyday commands. Run `make` (or `make help`) to list them. Run from the project root inside WSL.
VENV := venv/bin
MANAGE := $(VENV)/python manage.py

.DEFAULT_GOAL := help
.PHONY: help setup up down run migrate migrations shell test lint fix check lock upgrade sync openapi

help:  ## List the commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-11s %s\n", $$1, $$2}'

setup:  ## First-time setup: .env, virtualenv, services, database
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example; fill in its values, then run make setup again" && false)
	test -d venv || python -m venv venv
	$(VENV)/pip install --quiet --upgrade pip
	$(VENV)/pip install --quiet -r requirements.txt -r requirements-dev.txt
	docker compose up -d --wait
	$(MANAGE) migrate

up:  ## Start PostgreSQL and Redis (waits until they are healthy)
	docker compose up -d --wait

down:  ## Stop PostgreSQL and Redis (data is kept)
	docker compose down

run:  ## Start the development server: http://localhost:8000/api/docs
	$(MANAGE) runserver

migrate:  ## Apply database migrations
	$(MANAGE) migrate

migrations:  ## Create migrations for model changes (read them before committing)
	$(MANAGE) makemigrations

shell:  ## Open a Django shell with the models imported
	$(MANAGE) shell

test:  ## Run the tests. Pass options with ARGS, e.g. make test ARGS="-k routes"
	$(VENV)/pytest $(ARGS)

lint:  ## Report code problems
	$(VENV)/ruff check .

fix:  ## Fix the code problems Ruff can repair (import order, unused imports, ...)
	$(VENV)/ruff check --fix .

check:  ## Everything CI checks: lint, Django checks, missing migrations, tests
	$(VENV)/ruff check .
	$(MANAGE) check
	$(MANAGE) makemigrations --check --dry-run --no-input
	$(VENV)/pytest

lock:  ## Recompile the lockfiles after editing a requirements*.in file, then sync
	$(VENV)/pip-compile --quiet --strip-extras requirements.in
	$(VENV)/pip-compile --quiet --strip-extras requirements-dev.in
	$(VENV)/pip-sync requirements.txt requirements-dev.txt

upgrade:  ## Upgrade every dependency to its newest compatible version, then sync
	$(VENV)/pip-compile --quiet --strip-extras --upgrade requirements.in
	$(VENV)/pip-compile --quiet --strip-extras --upgrade requirements-dev.in
	$(VENV)/pip-sync requirements.txt requirements-dev.txt

sync:  ## Make the virtualenv match the lockfiles exactly
	$(VENV)/pip-sync requirements.txt requirements-dev.txt

openapi:  ## Regenerate docs/openapi.json from the code
	$(MANAGE) export_openapi_schema --api cs_cas.api.api --indent 2 --output docs/openapi.json

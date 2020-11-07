SHELL=/bin/bash

HAS_PIPENV = $(shell which pipenv && echo 'true' || echo 'false')

ifneq ("$(HAS_PIPENV)", "false")
	PYTHON = pipenv run python
else
	PYTHON = python
endif


.DEFAULT_GOAL := all

## help: Display list of commands (from gazr.io)
.PHONY: help
help: Makefile
	@sed -n 's|^##||p' $< | column -t -s ':' | sed -e 's|^| |'

## all: Run all targets
.PHONY: all
all: init style test build

## init: Install required depedencies
.PHONY: init
init:
	pipenv install --deploy

## init-dev: Install development depedencies
.PHONY: init-dev
init-dev:
	pipenv install --deploy --dev
	pipenv run pre-commit install -t pre-commit
	pipenv run pre-commit install -t prepare-commit-msg
	pipenv run pre-commit install -t commit-msg

## clean: Remove app environment and temporary files
.PHONY: clean
clean:
	pipenv --rm || true
	rm -f *.log || true
	rm -rf ".venv" || true
	rm -rf coverage.xml junit-coverage.xml || true
	pipenv run pre-commit uninstall -t pre-commit
	pipenv run pre-commit uninstall -t prepare-commit-msg
	pipenv run pre-commit uninstall -t commit-msg

## style: Check lint, code styling rules, format code
.PHONY: style
style:
	pipenv run pre-commit run --all-files

## test: Launch all tests
.PHONY: test
test:
	$(PYTHON) manage.py test

## run: Locally run the development server
.PHONY: run
run:
	$(PYTHON) manage.py runserver

## build: Build the Docker application
.PHONY: build
build:
	docker build --pull --rm \
		--target app \
		--tag woolly-api:dev \
		--file Dockerfile \
		.

## db-migrate: Apply all migrations to database
.PHONY: db-migrate
db-migrate:
	$(PYTHON) manage.py migrate
	# Initiate default values
	$(PYTHON) manage.py init_defaults all
	# Get all associations with fun_id in database
	$(PYTHON) manage.py fetch_fun_ids --report

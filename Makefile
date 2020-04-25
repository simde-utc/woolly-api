# TODO Check for environment
PYTHON?=python


init:
	$(PYTHON) -m pip install -qr requirements.txt
	$(PYTHON) manage.py migrate
	$(PYTHON) manage.py init_defaults all

init-dev:
	$(PYTHON) -m pip install -qr requirements-dev.txt

dev:
	$(PYTHON) manage.py runserver

test:
	$(PYTHON) manage.py test

lint:
	$(PYTHON) -m flake8 .


COMMANDS = init init-dev dev test lint

.PHONY: $(COMMANDS)
.SILENT: $(COMMANDS)
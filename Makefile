.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .pytest_cache
	rm -f .coverage

PIPENV := $(shell command -v pipenv 2> /dev/null)

init:
ifndef PIPENV
	$(error "dot is not available please install graphviz")
endif
	@echo "Pipenv found in PATH. You may now run \033[1mmake install"

lint: ## reformat with black
	pipenv run black snpit tests

test: ## run tests
	pipenv run pytest

coverage: ## check code coverage quickly with the default Python
	pipenv run coverage run --source snpit -m pytest
	pipenv run coverage report -m
	pipenv run coverage html
	pipenv run $(BROWSER) htmlcov/index.html

release: clean lint ## package and upload a release
	pipenv run python setup.py sdist upload
	pipenv run python setup.py bdist_wheel upload

dist: clean lint ## builds source and wheel package
	pipenv run python setup.py sdist
	pipenv run twine upload -r pypi dist/`ls -t dist | head -1`


install: clean ## install the package within your pipenv
	pipenv install --pre --dev
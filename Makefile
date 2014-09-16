## Standard makefile for Python tests

BASE_PACKAGE = datacat
PYTEST_ARGS = -vvv --pep8 --cov=$(BASE_PACKAGE) --cov-report=term-missing

.PHONY: all upload

all: help

help:
	@echo "AVAILABLE TARGETS"
	@echo "----------------------------------------"
	@echo "pypi_upload - build source distribution and upload to pypi"
	@echo "pypi_register - register proejct on pypi"
	@echo
	@echo "install - install project in production mode"
	@echo "install_dev - install project in development mode"
	@echo
	@echo "check (or 'test') - run tests"
	@echo "setup_tests - install dependencies for tests"
	@echo
	@echo "docs - build documentation (HTML)"
	@echo "publish_docs - publish documentation to GitHub pages"

pypi_register:
	python setup.py register -r https://pypi.python.org/pypi

pypi_upload:
	python setup.py sdist upload -r https://pypi.python.org/pypi

install:
	python setup.py install

develop: install_dev setup_tests setup_docs

install_dev:
	python setup.py develop

check: test

test: test_core test_plugins

test_core:
	py.test $(PYTEST_ARGS) ./tests/core

test_plugins:
	py.test $(PYTEST_ARGS) ./tests/plugins

setup_tests: tests/data
	pip install pytest pytest-pep8 pytest-cov mock

tests/data:
	git clone https://github.com/rshk/datacat-poc-140825-testdata/ tests/data

update_test_data: tests/data
	cd tests/data && git pull

docs:
	$(MAKE) -C docs html

setup_docs:
	pip install sphinx sphinx-rtd-theme

publish_docs: docs
	ghp-import -n -p ./docs/build/html
	@echo
	@echo "HTML output published on github-pages"

cleanup:
	find -name '*~' -print0 | xargs -0 rm -rfv
	find -name '*.pyc' -print0 | xargs -0 rm -rfv
	find -name __pycache__ -print0 | xargs -0 rm -rfv

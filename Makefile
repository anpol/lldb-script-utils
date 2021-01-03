# This file is to support the development workflow.
#
# Use `make <tool>` command to run a development tool.  Normally you should
# start with `make init` before doing everything else.
#
# Workflow commands:
#
# - `make init`: install dependencies, switch to "editable" mode.
# - `make edit`: install this package in "editable" mode.
# - `make unedit`: uninstall while being installed in "editable" mode.
# - `make format`: reformat source code according to style.
# - `make lint`: check source code for issues.
# - `make test`: run tests against installed packages.
# - `make dists`: create distribution packages.

.PHONY: all format lint test \
	deps deps-devel init edit unedit \
	dists sdist bdist bdist_wheel

all: format lint test

deps:
	pip install -r requirements.txt

deps-devel: deps
	pip install -r requirements-devel.txt

init:

ifdef VIRTUAL_ENV
init: deps-devel edit
endif

edit:
	pip install --editable "$(CURDIR)"

unedit:
	python setup.py develop --uninstall

format:
	yapf -ir "$(CURDIR)"

lint:
	pylint_runner --rcfile "$(CURDIR)/.pylintrc"

test:
	nosetests -v "$(CURDIR)"

dists: sdist bdist wheels

sdist: requirements
	python setup.py sdist

bdist: requirements
	python setup.py bdist

wheels: requirements
	python setup.py bdist_wheel

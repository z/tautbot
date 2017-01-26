#
# Project:   captions-server
# Copyright: (c) 2017 by Four Foot One <dev@fourfootone.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# A GNU Makefile for the project.
#

.PHONY: help clean lint docs tests tests-coverage

help:
	@echo "Use \`make <target>', where <target> is one of the following:"
	@echo "  clean          - remove all generated files"
	@echo "  lint           - check code style with flake8"
	@echo "  docs           - make docs"

clean:
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.py[co]' -exec rm -f {} +

lint:
	@flake8 --ignore=E221,E501,F401,F841,E128,D100,D101,D102,D104,D203,D204,D205,D400 tautbot/*.py

docs: docs/
	@cd docs && $(MAKE) html

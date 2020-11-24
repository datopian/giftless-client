# Makefile for giftless-client
PACKAGE_NAME := giftless_client
PACKAGE_DIRS := giftless_client
TESTS_DIR := tests

SHELL := bash
PYTHON := python
PIP := pip
PIP_COMPILE := pip-compile
PYTEST := pytest
GIT := git

PYTEST_EXTRA_ARGS :=

VERSION := $(shell $(PYTHON) -c 'import $(PACKAGE_NAME) as p; print(p.__version__)')
SOURCE_FILES := $(shell find $(PACKAGE_DIRS) $(TESTS_DIR) -type f -name "*.py")
SENTINELS := .make-cache
DIST_DIR := dist

default: help

## Regenerate requirements files
requirements: $(SENTINELS)/requirements

## Run all tests
test: dev-requirements.txt
	$(PIP) install -r dev-requirements.txt -e .
	$(PYTEST) $(PYTEST_EXTRA_ARGS) $(PACKAGE_DIRS) $(TESTS_DIR)

## Tag and push a release
release: $(SENTINELS)/dist
	@echo
	@echo "You are about to release $(PACKAGE_NAME) version $(VERSION)"
	@echo "This will:"
	@echo " - Create and push a git tag v$(VERSION)"
	@echo " - Create a release package and upload it to pypi"
	@echo
	@echo "Continue? (hit Enter or Ctrl+C to stop"
	@read
	$(GIT) tag v$(VERSION)
	$(GIT) push --tags
	$(PYTHON) -m twine upload dist/*

## Clean all generated files
distclean:
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -rf $(SENTINELS)/dist

## Create distribution files to upload to pypi
dist: $(SENTINELS)/dist

.PHONY: test release dist distclean requirements

requirements.txt: requirements.in
	$(PIP_COMPILE) --no-emit-index-url --output-file=requirements.txt requirements.in

dev-requirements.txt: dev-requirements.in
	$(PIP_COMPILE) --no-emit-index-url --output-file=dev-requirements.txt dev-requirements.in

$(SENTINELS):
	mkdir $@

$(SENTINELS)/dist-setup: | $(SENTINELS)
	$(PIP) install -U pip wheel twine
	@touch $@

$(SENTINELS)/dist: $(SENTINELS)/dist-setup $(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION).tar.gz $(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION)-py2.py3-none-any.whl | $(SENTINELS)
	@touch $@

$(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION).tar.gz $(DIST_DIR)/$(PACKAGE_NAME)-$(VERSION)-py2.py3-none-any.whl: $(SOURCE_FILES) setup.py | $(SENTINELS)/dist-setup
	$(PYTHON) setup.py sdist bdist_wheel --universal

$(SENTINELS)/requirements: dev-requirements.txt requirements.txt | $(SENTINELS)
	@touch $@

# Help related variables and targets

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM := 20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	  helpMessage = match(lastLine, /^## (.*)/); \
	  if (helpMessage) { \
	    helpCommand = substr($$1, 0, index($$1, ":")-1); \
	    helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
	    printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
	  } \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

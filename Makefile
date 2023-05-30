POETRY = poetry
SRC_DIR = src
TEST_DIR = tests
DIST_DIR = dist build
PYPI_REPO = https://test.pypi.org/legacy/

.PHONY: all clean test-all build install

all: clean test-all build

clean:
	@rm -rf $(DIST_DIR)

test-all:
	@$(POETRY) run tox -p -s

test:
	@$(POETRY) run tox -e python3.8

build:
	@$(POETRY) build

install:
	@$(POETRY) install

upload:
	@$(POETRY) install twine
	@$(POETRY) publish -r $(PYPI_REPO)

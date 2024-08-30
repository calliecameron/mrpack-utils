.PHONY: all
all: lint test

.PHONY: lint
lint:
	ruff check .
	ruff format --diff .
	mypy --strict .

.PHONY: test
test: testdata
	pytest --cov-report=term-missing --cov=mrpack_utils tests

.PHONY: testdata
testdata: testdata/test1.mrpack

TESTDATA1 := $(shell find testdata/test1 -type f -printf '%P\n')
TESTDATA1_DEPS := $(addprefix testdata/test1/,$(TESTDATA))

testdata/test1.mrpack: $(TESTDATA1_DEPS)
	cd testdata/test1 && zip test1.mrpack $(TESTDATA1) && mv test1.mrpack ..

SUBDIR_ROOTS := mrpack_utils testdata tests
DIRS := . $(shell find $(SUBDIR_ROOTS) -type d)
CLEAN_PATTERNS := *~ .*~ *.pyc .mypy_cache __pycache__
CLEAN := $(foreach DIR,$(DIRS),$(addprefix $(DIR)/,$(CLEAN_PATTERNS)))

.PHONY: clean
clean:
	rm -rf $(CLEAN) testdata/*.mrpack

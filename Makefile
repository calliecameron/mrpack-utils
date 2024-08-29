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
testdata: testdata/test.mrpack

TESTDATA := $(shell find testdata -type f ! -name test.mrpack -printf '%P\n')
TESTDATA_DEPS := $(addprefix testdata/,$(TESTDATA))

testdata/test.mrpack: $(TESTDATA_DEPS)
	cd testdata && zip test.mrpack $(TESTDATA)

SUBDIR_ROOTS := mrpack_utils testdata tests
DIRS := . $(shell find $(SUBDIR_ROOTS) -type d)
CLEAN_PATTERNS := *~ .*~ *.pyc .mypy_cache __pycache__
CLEAN := $(foreach DIR,$(DIRS),$(addprefix $(DIR)/,$(CLEAN_PATTERNS)))

.PHONY: clean
clean:
	rm -rf $(CLEAN) testdata/test.mrpack

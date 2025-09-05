.PHONY: all
all: lint test

.PHONY: lint
lint:
	uv run ruff check .
	uv run ruff format --diff .
	uv run mypy --strict .

.PHONY: test
test: testdata
	uv run pytest --cov-report=term-missing --cov=mrpack tests

.PHONY: testdata
testdata: testdata/test1.mrpack testdata/test2.mrpack testdata/bad1.mrpack

TESTDATA1 := $(shell find testdata/test1 -type f -printf '%P\n')
TESTDATA1_DEPS := $(addprefix testdata/test1/,$(TESTDATA))

testdata/test1.mrpack: $(TESTDATA1_DEPS)
	cd testdata/test1 && zip ../test1.mrpack $(TESTDATA1)

TESTDATA2 := $(shell find testdata/test2 -type f -printf '%P\n')
TESTDATA2_DEPS := $(addprefix testdata/test2/,$(TESTDATA))

testdata/test2.mrpack: $(TESTDATA2_DEPS)
	cd testdata/test2 && zip ../test2.mrpack $(TESTDATA2)

TESTDATA_BAD1 := $(shell find testdata/bad1 -type f -printf '%P\n')
TESTDATA_BAD1_DEPS := $(addprefix testdata/bad1/,$(TESTDATA))

testdata/bad1.mrpack: $(TESTDATA_BAD1_DEPS)
	cd testdata/bad1 && zip ../bad1.mrpack $(TESTDATA_BAD1)

.PHONY: clean
clean:
	rm -f .coverage testdata/*.mrpack
	find . -depth '(' -type d '(' -name '.mypy_cache' -o -name '.ruff_cache' -o -name '.pytest_cache' -o -name '__pycache__' ')' ')' -exec rm -r '{}' ';'
	find . '(' -type f -name '*~' ')' -delete

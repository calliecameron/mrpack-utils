MAKEFLAGS += --no-builtin-rules --no-builtin-variables

.PHONY: all
all: precommit

.PHONY: deps
deps: .deps-installed

.deps-installed: pyproject.toml uv.lock package.json package-lock.json .pre-commit-config.yaml .template_files/pre_push
	.template_files/uv_install_deps
	.template_files/npm_install_deps
	.template_files/pre_commit_install
	touch .deps-installed

# We run each 'update_deps' step twice, before and after updating the interpreter,
# in case existing package versions aren't compatible with the new interpreter.
.PHONY: deps_update
deps_update: deps
	.template_files/uv_update_deps
	.template_files/uv_update_python
	.template_files/uv_update_deps
	.template_files/npm_update_deps
	.template_files/npm_update_node
	.template_files/npm_update_deps
	uv run pre-commit autoupdate
	uv run gha-update

.PHONY: precommit
precommit: deps
	uv run pre-commit run -a

.PHONY: ci
ci: precommit test_slow

# Fast tests are run by pre-commit
.PHONY: test_fast
test_fast: deps testdata
	uv run pytest -m 'not slow' tests
	uv run ast-grep test --update-all

# Slow tests are only run in CI
.PHONY: test_slow
test_slow: deps testdata
	uv run pytest -m slow tests

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

.PHONY: template_reapply
template_reapply: deps
	uv run copier update --trust --vcs-ref=:current:

.PHONY: template_update
template_update: deps
	uv run copier update --trust

.PHONY: clean
clean:
	find . '(' -type f -name '*~' ')' -delete
	rm -f .deps-installed
	rm -f testdata/*.mrpack

.PHONY: deepclean
deepclean: clean
	rm -rf .venv
	rm -rf node_modules
	find . -depth '(' -type d -name '__pycache__' ')' -exec rm -r '{}' ';'
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf .pytest_cache .coverage

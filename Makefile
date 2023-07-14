.PHONY: all
all: lint test

.PHONY: lint
lint:
	pylint --score n --recursive y .
	flake8 '--filename=*.py,*.pyi'
	black --check .
	isort --check .
	mypy --strict .

.PHONY: test
test: testdata
	pytest --cov-report=term-missing --cov=mrcheck mrcheck_test.py

.PHONY: testdata
testdata: testdata/test.mrpack

testdata/test.mrpack: testdata/modrinth.index.json
	cd testdata && zip test.mrpack modrinth.index.json

.PHONY: clean
clean:
	rm -rf *~ __pycache_ testdata/test.mrpack_

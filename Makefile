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
test:
	pytest --cov-report=term-missing --cov=mrcheck mrcheck_test.py

.PHONY: clean
clean:
	rm -rf *~ __pycache__

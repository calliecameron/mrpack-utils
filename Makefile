.PHONY: all
all: lint

.PHONY: lint
lint:
	pylint --score n --recursive y .
	flake8 '--filename=*.py,*.pyi'
	black --check .
	isort --check .
	mypy --strict .

.PHONY: clean
clean:
	rm -rf *~ __pycache__

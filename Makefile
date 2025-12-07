.PHONY: install dev test format lint

install:
	pip install -r requirements.txt

lint:
	black --check .
	test -f requirements-dev.txt && flake8 . || true

format:
	black .

test:
	pytest -v

dev: install
	pip install -r requirements-dev.txt

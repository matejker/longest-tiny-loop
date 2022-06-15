TEST_PATH=./tests
MIN_COVERAGE=80

.PHONY: requirements
requirements:
	poetry install --no-dev

.PHONY: requirements_tools
requirements_tools:
	poetry install

.PHONY: lint
lint: requirements_tools
	poetry run flake8
	poetry run black --check .
	poetry run bandit .

.PHONY: test
test: requirements_tools
	poetry run pytest -vv --color=yes $(TEST_ONLY)

.PHONY: coverage
coverage:
	poetry run pytest --cov longest_tiny_loop --cov-fail-under=$(MIN_COVERAGE) $(TEST_ONLY)

.PHONY: format
format: requirements_tools
	poetry run black .

.PHONY: typecheck
typecheck: requirements_tools
	poetry run mypy tests longest_tiny_loop

.PHONY: notebook
notebook: requirements
	poetry run jupyter notebook
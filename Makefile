.PHONY: install lint format typecheck test coverage clean

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=effect_log --cov-report=term-missing --cov-report=html

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

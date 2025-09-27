.PHONY: install check-lint format typecheck test coverage clean fix-lint actions-list actions-ci actions-security actions-publish actions-release actions-all

install:
	poetry install

check-lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=effect_log --cov-report=term-missing --cov-report=html

fix-lint:
	poetry run ruff format .
	poetry run ruff check . --fix

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

# GitHub Actions local testing
actions-list:
	@echo "Available GitHub Actions:"
	@echo "  ci: Main CI pipeline (lint, test, type-check)"
	@echo "  security: Security vulnerability scanning"
	@echo "  publish: Publish to PyPI"
	@echo "  release: Create release"
	@echo ""
	@echo "Usage:"
	@echo "  make actions-ci       # Test CI workflow"
	@echo "  make actions-security # Test security workflow"
	@echo "  make actions-publish  # Test publish workflow"
	@echo "  make actions-release  # Test release workflow"
	@echo "  make actions-all      # Test main workflows"

actions-ci:
	@echo "Testing CI workflow..."
	act push -j test --container-architecture linux/amd64 --secret-file .secrets --matrix python-version:3.11 --matrix os:ubuntu-latest

actions-security:
	@echo "Testing security workflow..."
	act workflow_dispatch -W .github/workflows/security.yaml --container-architecture linux/amd64 --secret-file .secrets

actions-publish:
	@echo "Testing publish workflow..."
	act workflow_dispatch -W .github/workflows/publish.yaml --container-architecture linux/amd64 --secret-file .secrets

actions-release:
	@echo "Testing release workflow..."
	act workflow_dispatch -W .github/workflows/release.yaml --container-architecture linux/amd64 --secret-file .secrets

actions-all: actions-ci actions-security
	@echo "Main workflows tested!"

# LinkedIn Ghost Jobs ETL Pipeline - Makefile
# Professional development and deployment automation

.PHONY: help install install-dev test test-coverage lint format clean build docker-build docker-run setup-dev docs serve-docs

# Default target
help:
	@echo "LinkedIn Ghost Jobs ETL Pipeline - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  setup-dev     Complete development environment setup"
	@echo "  format        Format code with black and isort"
	@echo "  lint          Run code quality checks"
	@echo "  test          Run test suite"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Pipeline Operations:"
	@echo "  init-db       Initialize database"
	@echo "  run-etl       Execute complete ETL pipeline"
	@echo "  extract       Extract data only"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run pipeline in Docker"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          Generate documentation"
	@echo "  serve-docs    Serve documentation locally"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Clean temporary files"
	@echo "  build         Build distribution packages"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

setup-dev: install-dev
	@echo "Setting up development environment..."
	python -m playwright install
	mkdir -p data/{raw,transformed,outputs}
	mkdir -p logs
	@echo "Development environment ready!"

# Code quality targets
format:
	black src/ tests/ *.py
	isort src/ tests/ *.py

lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/

# Testing targets
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Pipeline operations
init-db:
	python src/main.py init_db

run-etl:
	python src/main.py run_etl

extract:
	python src/main.py extract

# Docker targets
docker-build:
	docker build -t linkedin-ghost-jobs-etl .

docker-run:
	docker-compose up --build

# Documentation targets
docs:
	sphinx-build -b html docs/ docs/_build/

serve-docs:
	python -m http.server 8000 --directory docs/_build/

# Maintenance targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

build: clean
	python -m build

# CI/CD targets
ci-test: install-dev lint test-coverage

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	# Add your deployment commands here
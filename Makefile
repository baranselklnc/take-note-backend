# Take Note Backend API Makefile

.PHONY: help install dev test lint clean docker-build docker-run setup seed-db

# Default target
help:
	@echo "Take Note Backend API - Available Commands:"
	@echo ""
	@echo "  install      Install dependencies"
	@echo "  dev          Run development server"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  clean        Clean up cache files"
	@echo "  setup        Setup database"
	@echo "  seed-db      Seed database with sample data"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	python run.py

# Run tests
test:
	pytest test_main.py -v

# Run tests with coverage
test-coverage:
	pytest test_main.py --cov=main --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Clean up cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

# Setup database
setup:
	python scripts/setup_db.py

# Seed database with sample data
seed-db:
	python scripts/seed_data.py

# Build Docker image
docker-build:
	docker build -t take-note-backend .

# Run with Docker Compose
docker-run:
	docker-compose up --build

# Run with Docker Compose in background
docker-run-detached:
	docker-compose up --build -d

# Stop Docker Compose
docker-stop:
	docker-compose down

# View Docker logs
docker-logs:
	docker-compose logs -f

# Production deployment
deploy:
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Check application health
health:
	curl -f http://localhost:8000/health || echo "❌ Health check failed"

# Format code
format:
	black .
	isort .

# Type checking
type-check:
	mypy main.py config.py database.py models.py auth.py

# Security check
security:
	bandit -r . -f json -o security-report.json
	@echo "Security report saved to security-report.json"

# Full check (lint, test, type-check, security)
check: lint test type-check security
	@echo "✅ All checks passed!"

# Development setup
dev-setup: install setup
	@echo "🎉 Development environment ready!"
	@echo "Run 'make dev' to start the server"
	@echo "Visit http://localhost:8000/docs for API documentation"

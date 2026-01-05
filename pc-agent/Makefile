.PHONY: help install dev-install run test lint format clean docker-up docker-down migrate scrape

help:
	@echo "PC Build Recommendation System - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make dev-install    Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run            Run FastAPI development server"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo ""
	@echo "Database:"
	@echo "  make init-db        Initialize database"
	@echo "  make migrate        Run database migrations"
	@echo "  make migration      Create new migration"
	@echo ""
	@echo "Scraping:"
	@echo "  make scrape-all     Scrape all components"
	@echo "  make scrape-gpu     Scrape GPUs only"
	@echo ""
	@echo "Celery:"
	@echo "  make celery-worker  Start Celery worker"
	@echo "  make celery-beat    Start Celery beat"
	@echo "  make flower         Start Flower monitoring"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      Start all services with Docker Compose"
	@echo "  make docker-down    Stop all services"
	@echo "  make docker-logs    View logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Clean cache and temporary files"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-cov black ruff mypy

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	gunicorn app.main:app \
		--workers 4 \
		--worker-class uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000 \
		--timeout 120

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/
	mypy app/

format:
	black app/
	ruff check --fix app/

init-db:
	python scripts/init_db.py

migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

scrape-all:
	python scripts/run_scraper.py all --pages 5

scrape-gpu:
	python scripts/run_scraper.py gpu --pages 10

scrape-cpu:
	python scripts/run_scraper.py cpu --pages 10

celery-worker:
	celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2

celery-beat:
	celery -A app.tasks.celery_app beat --loglevel=info

flower:
	celery -A app.tasks.celery_app flower --port=5555

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-build:
	docker-compose build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

.DEFAULT_GOAL := help


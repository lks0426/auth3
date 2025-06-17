.PHONY: help build up down logs clean test lint backend-test backend-lint frontend-test frontend-lint migrate dev-setup

help:
	@echo "Available commands:"
	@echo "  build          Build docker images for dev environment"
	@echo "  up             Start dev environment (docker-compose up)"
	@echo "  down           Stop dev environment (docker-compose down)"
	@echo "  logs           Follow logs for dev services"
	@echo "  clean          Remove docker volumes and build artifacts"
	@echo "  test           Run all tests"
	@echo "  lint           Run all linters"
	@echo "  backend-test   Run backend tests"
	@echo "  backend-lint   Run backend linters"
	@echo "  frontend-test  Run frontend tests"
	@echo "  frontend-lint  Run frontend linters"
	@echo "  migrate        Run database migrations"
	@echo "  dev-setup      Run development environment setup script"

# Default to dev environment for compose commands
COMPOSE_FILE := docker-compose.dev.yml
COMPOSE_PROD_FILE := docker-compose.prod.yml

build:
	docker-compose -f $(COMPOSE_FILE) build

up:
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	docker-compose -f $(COMPOSE_FILE) down

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

clean: down
	docker volume rm $$(docker volume ls -qf name=auth-system_postgres_dev_data) || true
	# Add commands to clean backend/frontend build artifacts if any (e.g. backend/dist, frontend/dist)
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist

# --- Test & Lint Commands ---
backend-test:
	docker-compose -f $(COMPOSE_FILE) exec backend pytest app/tests

backend-lint:
	docker-compose -f $(COMPOSE_FILE) exec backend flake8 .
	docker-compose -f $(COMPOSE_FILE) exec backend black . --check
	docker-compose -f $(COMPOSE_FILE) exec backend mypy .

frontend-test:
	docker-compose -f $(COMPOSE_FILE) exec frontend npm run test

frontend-lint:
	docker-compose -f $(COMPOSE_FILE) exec frontend npm run lint
	docker-compose -f $(COMPOSE_FILE) exec frontend npm run type-check

test: backend-test frontend-test
lint: backend-lint frontend-lint

# --- Other Commands ---
migrate:
	docker-compose -f $(COMPOSE_FILE) exec backend alembic upgrade head

dev-setup:
	./scripts/dev-setup.sh

# Example for production environment (use with caution)
build-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) build

up-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) up -d

down-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) down

logs-prod:
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

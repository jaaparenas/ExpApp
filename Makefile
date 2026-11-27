.PHONY: help backend-install backend-test backend-migrate backend-run backend-lint frontend-install frontend-dev frontend-build e2e

help:
	@echo "backend-install  Create the venv and install dependencies"
	@echo "backend-test     Run backend tests"
	@echo "backend-migrate  Apply database migrations"
	@echo "backend-run      Start the API on :5000"
	@echo "backend-lint     Run bandit and pip-audit"
	@echo "frontend-install Install frontend dependencies"
	@echo "frontend-dev     Start Nuxt on :3000"
	@echo "frontend-build   Build the frontend"
	@echo "e2e              Run headless Playwright tests"

backend-install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

backend-test:
	cd backend && .venv/bin/python -m unittest discover -s tests -p 'test*.py' -v

backend-migrate:
	cd backend && .venv/bin/flask --app server db upgrade

backend-run:
	cd backend && .venv/bin/flask --app server run --debug

backend-lint:
	cd backend && .venv/bin/bandit -q -r app server.py config.py
	cd backend && .venv/bin/pip-audit -r requirements.txt

frontend-install:
	cd frontend/nuxt && npm ci

frontend-dev:
	cd frontend/nuxt && npm run dev

frontend-build:
	cd frontend/nuxt && npm run build

e2e:
	cd frontend/nuxt && npx playwright test

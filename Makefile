.PHONY: up down logs migrate backend-test backend-run frontend-install frontend-run frontend-build

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	docker compose exec api alembic upgrade head

backend-test:
	cd backend && python3 -m pytest -q

backend-run:
	cd backend && uvicorn app.main:app --reload

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

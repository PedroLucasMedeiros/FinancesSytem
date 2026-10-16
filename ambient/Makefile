.PHONY: up down build logs migrate shell

up: build
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

build:
	docker compose -f docker-compose.yml build

logs:
	docker compose -f docker-compose.yml logs -f

migrate:
	docker compose -f docker-compose.yml exec web python manage.py migrate

shell:
	docker compose -f docker-compose.yml exec web python manage.py shell
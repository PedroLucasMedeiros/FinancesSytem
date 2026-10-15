.PHONY: up down build logs migrate

up:
	docker compose -f docker-compose.yml up --build -d

down:
	docker compose -f docker-compose.yml down

logs:
	docker compose -f docker-compose.yml logs -f

migrate:
	docker compose -f docker-compose.yml exec web python manage.py migrate

shell:
	docker compose -f docker-compose.yml exec web python manage.py shell

---

### `Makefile`
```makefile
.PHONY: up down logs shell

up:
	cp .env.sample .env || true
	echo "Make sure to edit .env before running services (POSTGRES_PASSWORD)."
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

shell:
	docker compose exec streamlit /bin/sh

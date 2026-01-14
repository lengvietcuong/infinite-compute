```bash
docker compose build
```

```bash
docker compose up db -d && docker compose run --rm backend python -m database.initialize_database --env-file ./backend/.env
```

```bash
docker-compose --env-file ./backend/.env --env-file ./frontend/.env up
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

```bash
docker compose down
```
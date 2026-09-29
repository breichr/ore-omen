# Ore & Omen

Textbasiertes Multiplayer-Browsergame als PWA fürs Smartphone. Weird West, 1878. Design und Regeln: `docs/`, Einstieg über `CLAUDE.md`.

## Lokal starten

Voraussetzungen: Python 3.12 mit [uv](https://docs.astral.sh/uv/), Node 22, PostgreSQL 16 (oder Docker).

### Variante A: alles in Docker

```sh
cp .env.example .env        # OO_COOKIE_SECURE=false setzen, weil lokal ohne HTTPS
docker compose up --build
```

Dann http://localhost:8080 öffnen.

### Variante B: Entwicklung mit Hot Reload

```sh
# 1. Datenbank (Beispiel mit Docker)
docker run -d --name ore-db -p 5432:5432 \
  -e POSTGRES_USER=ore -e POSTGRES_PASSWORD=ore -e POSTGRES_DB=ore_omen postgres:16
docker exec ore-db createdb -U ore ore_omen_test   # für die Tests

# 2. API (http://localhost:8000)
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# 3. Worker (optional in M0)
uv run python -m app.worker

# 4. Frontend (http://localhost:5173, leitet /api an :8000 weiter)
cd frontend
npm install
npm run dev
```

Auf dem Handy im selben WLAN: `npm run dev -- --host` und die angezeigte IP öffnen. Den Service Worker und die Installation gibt es nur über HTTPS oder `localhost`. Zum Testen der Installation also deployen oder einen Tunnel nutzen.

## Tests und Lint

```sh
cd backend  && uv run pytest && uv run ruff check . && uv run ruff format --check .
cd frontend && npm test && npm run check && npm run lint
```

Die Backend-Tests brauchen PostgreSQL. Die Datenbank ist `ore_omen_test` auf localhost, anpassbar über `OO_TEST_DATABASE_URL`. Die Tests leeren diese Datenbank.

End-to-End-Abnahme (Registrieren → Charakter → Wiederöffnen → Offline), während API und Frontend laufen:

```sh
cd frontend && npm run build && npx vite preview --port 4173 &
BASE_URL=http://localhost:4173 node scripts/smoke.mjs
```

## Struktur

```
backend/app/game/     reine Spiellogik (constants.py, character.py, rounding.py)
backend/app/models/   SQLAlchemy · backend/alembic/ Migrationen
backend/app/api/      Routen · backend/app/services/ Logik mit DB
backend/app/worker/   Worker (ab M1 geplante Ereignisse)
frontend/src/lib/text/de.ts   alle UI-Texte
content/              Spielinhalte als Daten (ab M1)
tools/duel_sim.py     Duell-Referenz und Balancing-Simulator
```

Deployment: `docs/deploy.md`.

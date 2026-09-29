# 08 – Technik & Architektur

> Stack ist ein **Vorschlag**. Vor Projektstart mit dem Projektinhaber bestätigen (siehe „Offen“).

## Überblick

```
PWA (SvelteKit, static)  ──HTTPS/JSON──▶  API (FastAPI)  ──▶  PostgreSQL
        ▲                                      │
        │ Web Push                             ▼
        └──────────────────────────  Worker (Tick + Jobs)
```

- **Frontend**: SvelteKit mit `adapter-static`, Service Worker für Offline-Shell und Push
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, Pydantic
- **Datenbank**: PostgreSQL 16
- **Worker**: eigener Prozess, gleiche Codebasis, verarbeitet fällige Ereignisse
- **Push**: Web Push (VAPID) über `pywebpush`
- **Deployment**: Docker Compose, gehostet über Coolify auf einem VPS

## Repo-Struktur

```
ore-omen/
├── CLAUDE.md
├── docs/
├── content/              # Spielinhalte als Daten
│   ├── buildings.yaml
│   ├── items.yaml
│   ├── enemies.yaml
│   ├── quests/<faction>/*.json
│   └── whispers/*.json
├── backend/
│   ├── app/
│   │   ├── api/          # Routen
│   │   ├── game/         # Reine Spiellogik, ohne DB-Zugriff
│   │   │   ├── constants.py
│   │   │   ├── duel.py
│   │   │   ├── buildings.py
│   │   │   ├── reputation.py
│   │   │   ├── corruption.py
│   │   │   ├── bounty.py
│   │   │   └── quests.py
│   │   ├── models/       # SQLAlchemy
│   │   ├── services/     # Verbindet game/ mit DB
│   │   └── worker/       # Tick-Verarbeitung
│   ├── tests/
│   └── alembic/
├── frontend/
└── tools/
    └── duel_sim.py
```

**Regel**: `app/game/` enthält reine Funktionen (Eingabe → Ergebnis) ohne DB, ohne Zeitabfragen, ohne globalen Zufall. Zufall kommt als `random.Random(seed)` herein. Dadurch ist die gesamte Spiellogik ohne Datenbank testbar.

## Zeit und Timer

Kein Echtzeit-Server. Alles Zeitgesteuerte ist ein **geplantes Ereignis** mit Fälligkeitszeitpunkt.

```sql
scheduled_events(
  id, due_at timestamptz, kind text, payload jsonb,
  status text,            -- pending | done | failed
  created_at, processed_at
)
```

- Worker holt alle 5 s fällige Ereignisse mit `FOR UPDATE SKIP LOCKED` und verarbeitet sie in einer Transaktion
- Beispiele: `build_complete`, `job_complete`, `travel_arrive`, `injury_end`, `daily_reset`, `corruption_daily`, `weekly_influence`, `whisper_event`
- **Produktion** wird nicht getickt, sondern beim Lesen berechnet: `lager = min(kapazität, lager_bei_letzter_änderung + rate × Δt)`. Bei jeder Änderung (Bau, Überfall, Verbrauch) wird der Stand festgeschrieben.

## Datenmodell (Kern)

```
users(id, email, password_hash, created_at)
characters(id, user_id, name, class, level, xp,
           strength, dexterity, intellect, charisma, unspent_points,
           dollars, bank_dollars, corruption_tenths,
           region, status, status_until, created_at)
character_skills(character_id, skill, points)
duel_tactics(character_id, target_weights jsonb, move_weights jsonb)

buildings(character_id, type, level, damaged bool)
build_queue(id, character_id, type, target_level, started_at, finishes_at)
resources(character_id, name, amount, updated_at)      -- Stand zum Zeitpunkt updated_at

reputation(character_id, faction, value)
oaths(character_id, faction, sworn_at)

bounties(id, target_id, issuer_type, issuer_id, amount, created_at, closed_at)
duels(id, attacker_id, defender_id, seed, attacker_plan jsonb,
      result jsonb, log jsonb, created_at)

quest_instances(id, character_id, quest_id, seed, state, step, data jsonb,
                started_at, finishes_at)
items(id, character_id, item_id, equipped bool)
scars(character_id, scar_id, gained_at)

push_subscriptions(id, user_id, endpoint, keys jsonb, created_at)
server_state(key, value jsonb)                           -- Einfluss, Flags
```

## API (Auszug, REST)

```
POST /auth/register · /auth/login · /auth/logout
GET  /me                         Charakter + berechnete Werte + Timer
GET  /settlement                 Gebäude, Lager (live berechnet), Warteschlange
POST /settlement/build           {type}
GET  /quests/available
POST /quests/{id}/start
POST /quests/instances/{id}/choose   {option}
GET  /duels/targets              gültige Gegner in Stufenrange
POST /duels                      {defender_id, plan?}
GET  /duels/{id}                 Protokoll
PUT  /duels/tactics              Standardtaktik
GET  /bounties
POST /bounties                   Privatkopfgeld
GET  /factions                   Ruf, Stufen, Einfluss
POST /push/subscribe
```

Server gibt immer die **absoluten Endzeitpunkte** von Timern zurück, der Client zählt lokal herunter.

## Auth

- Session-Cookie (HttpOnly, Secure, SameSite=Lax), Passwort-Hash mit Argon2
- Rate-Limit auf Login und schreibende Endpunkte
- Ein Charakter pro Account (Mehrfachaccounts in den Nutzungsbedingungen verbieten)

## Anti-Cheat

- Keine Spielberechnung im Client
- Alle Aktionen prüfen Zustand serverseitig (Timer abgelaufen? Ressourcen vorhanden? Stufenrange?)
- Seeds werden serverseitig erzeugt und erst nach Auflösung an den Client gegeben

## PWA

- Manifest mit Name „Ore & Omen“, Kurzname „Ore & Omen“, dunkles Theme
- App-Shell offline verfügbar, Spielstand erfordert Verbindung (klare Offline-Anzeige)
- Push-Opt-in erst nach dem ersten Timer, nicht beim ersten Start
- Schrift: gut lesbare Serifenschrift für Erzähltext, serifenlose für UI

## Deployment

- `docker-compose.yml` mit `api`, `worker`, `db`, `frontend` (statisch via Caddy/nginx)
- Coolify übernimmt TLS und Domain
- Backups: tägliches `pg_dump`, 14 Tage Aufbewahrung
- Migrationen laufen beim Start des `api`-Containers

## Offen (vor Start klären)

1. Stack bestätigen: SvelteKit + FastAPI + Postgres, oder Alternative (z. B. Vue, Node)
2. Domain
3. Serverzeitzone für tägliche Resets (Vorschlag: Europe/Vienna, 04:00)
4. Spielersprache: nur Deutsch zum Start oder direkt i18n-fähig anlegen
5. Monetarisierung: keine / kosmetisch / Spenden

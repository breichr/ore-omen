# 08 – Technik & Architektur

> Stack vom Projektinhaber bestätigt (siehe „Entschieden“).

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

- Alle Zeitpunkte werden in **UTC** gespeichert.
- **Serverzeitzone**: `Europe/Vienna`. Tagesreset um **04:00**, Wochenwechsel **Montag 00:00**, jeweils Ortszeit Wien, sommerzeitfest über `zoneinfo` berechnet.
- Spielerbezogene Zeiten (z. B. „ab 20:00 Ortszeit“, Ruhezeiten für Push) nutzen `users.timezone` (IANA-Name, Standard `Europe/Vienna`).

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
users(id, username, username_key UNIQUE, password_hash, recovery_key_hash,
      timezone, created_at)                              -- username_key: lower(username)
sessions(id, user_id, token_hash, created_at, last_seen_at, expires_at,
         user_agent)                                     -- 30 Tage gleitend
characters(id, user_id UNIQUE, name, name_key UNIQUE, class,   -- name_key: casefold(name) level, xp,
           strength, dexterity, intellect, charisma,
           unspent_attribute_points, unspent_skill_points,
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
activities(id, character_id, kind, ref, data jsonb,   -- kind: job | travel
           started_at, finishes_at, status)
gangs(id, name, founder_id, created_at)
gang_members(gang_id, character_id, role, joined_at)
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

- Login mit **Benutzername + Passwort**. Keine E-Mail-Adresse.
  - Benutzername: 3–20 Zeichen, `A–Z a–z 0–9 _ -`; eindeutig ohne Beachtung der Groß-/Kleinschreibung. Unabhängig vom Charakternamen.
  - Passwort: 8–128 Zeichen.
- **Notfall-Wiederherstellungsschlüssel** statt Passwort-Reset per E-Mail:
  - Wird bei der Registrierung serverseitig erzeugt und **genau einmal** angezeigt. Gespeichert wird nur der Argon2-Hash.
  - Format: 25 Zeichen Crockford-Base32 in fünf Gruppen, z. B. `7K3QM-D9XHT-2VRPA-W8NCE-4FJ6B` (125 Bit). Eingabe ignoriert Groß-/Kleinschreibung, Leerzeichen und Bindestriche.
  - Wiederherstellen: Benutzername + Schlüssel + neues Passwort. Danach ist der alte Schlüssel ungültig, ein neuer wird einmal angezeigt, alle bestehenden Sessions werden beendet.
  - Neu erzeugen im Einstellungs-Screen: eingeloggt + aktuelles Passwort. Der alte Schlüssel wird ungültig, der neue einmal angezeigt. Sessions bleiben bestehen.
  - Wer Passwort und Schlüssel verliert, verliert das Konto (kein Support-Weg in M0).
- Session-Cookie (HttpOnly, Secure, SameSite=Lax) mit zufälligem Token; in `sessions` wird nur der SHA-256-Hash gespeichert. Laufzeit **30 Tage gleitend**: jede Anfrage verlängert `expires_at`. Logout löscht die Session serverseitig.
- Passwort-Hash mit Argon2
- Rate-Limit auf Login, Registrierung, Wiederherstellung und schreibende Endpunkte
- Ein Charakter pro Account (Mehrfachaccounts in den Nutzungsbedingungen verbieten)
- Charaktername: 3–20 Zeichen, Buchstaben inkl. Umlaute, Leerzeichen, Bindestrich, Apostroph; eindeutig ohne Beachtung der Groß-/Kleinschreibung

## Rundung

Überall **ROUND_HALF_UP** über `decimal`, bei negativen Werten auf den Betrag angewendet (−1,5 → −2, −2,4 → −2). Eine zentrale Hilfsfunktion in `app/game/`, nie Pythons `round()` (Banker's Rounding). Verderbnis wird in Zehnteln gespeichert.

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

## Entschieden

1. **Stack**: SvelteKit (static) + FastAPI + PostgreSQL
2. **Domain**: noch keine. Bis dahin `docker-compose.yml` + Deploy-Anleitung (`docs/deploy.md`)
3. **Zeitzone**: Europe/Vienna, Reset 04:00, Wochenwechsel Montag 00:00, Speicherung in UTC
4. **Sprache**: nur Deutsch. Alle UI-Texte zentral in `frontend/src/lib/text/de.ts`
5. **Monetarisierung**: keine bis nach der Beta

## Offen

*(derzeit nichts)*

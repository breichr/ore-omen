# Deployment (Coolify)

Stand M0. Noch keine Domain festgelegt (`08-technik.md`, „Entschieden“). Diese Anleitung gilt, sobald ein VPS mit Coolify und eine Domain bereitstehen.

## Aufbau

`docker-compose.yml` im Repo-Root startet vier Dienste:

| Dienst | Image | Aufgabe |
|---|---|---|
| `db` | `postgres:16-alpine` | Datenbank, Volume `db-data` |
| `api` | `backend/Dockerfile` | FastAPI; führt beim Start `alembic upgrade head` aus |
| `worker` | `backend/Dockerfile` | `python -m app.worker`, startet erst, wenn `api` gesund ist |
| `frontend` | `frontend/Dockerfile` | Caddy liefert die PWA aus und leitet `/api/*` an `api:8000` weiter |

Nach außen ist nur `frontend` (Port 80 im Container, über den Coolify-Proxy) sichtbar. PWA und API laufen unter derselben Origin, deshalb braucht das Session-Cookie kein CORS.

## Einrichten in Coolify

1. **New Resource → Docker Compose**, dieses Git-Repository und den Branch wählen. Compose-Datei: `docker-compose.yml`.
2. **Umgebungsvariablen** setzen (Vorlage: `.env.example`):
   - `POSTGRES_PASSWORD`: langes Zufallspasswort
   - `OO_COOKIE_SECURE=true` (Standard)
   - `POSTGRES_USER` und `POSTGRES_DB` können auf dem Standard bleiben
3. **Domain** beim Dienst `frontend` eintragen (z. B. `https://spiel.example.com:80`, also Domain plus Container-Port `80`). Coolify leitet über seinen Proxy weiter und holt das TLS-Zertifikat. `docker-compose.yml` veröffentlicht bewusst **keinen** Host-Port: Ein fester Port wie 8080 kollidiert mit anderen Anwendungen auf dem Server (`Bind for 0.0.0.0:8080 failed: port is already allocated`). Den Port für lokale Läufe setzt `docker-compose.override.yml`, das Coolify nicht lädt.
4. **Deploy**. Danach prüfen:
   - `https://<domain>/api/health` → `{"status":"ok","db":"ok"}`
   - Startseite öffnet den Login, auf dem Handy erscheint „App installieren“ (Android) bzw. der Hinweis „Zum Home-Bildschirm“ (iOS)
5. **Backups**: In Coolify für die Datenbank ein tägliches Backup (`pg_dump`) mit 14 Tagen Aufbewahrung einrichten (`08-technik.md`, „Deployment“). Alternativ per Cron auf dem VPS:
   ```sh
   docker compose exec -T db pg_dump -U ore ore_omen | gzip > /backups/ore_omen_$(date +%F).sql.gz
   find /backups -name 'ore_omen_*.sql.gz' -mtime +14 -delete
   ```

## Wichtig

- Web Push (M4) und Service Worker brauchen **HTTPS**. Unter plain HTTP funktioniert die PWA nur auf `localhost`.
- Die API vertraut `X-Forwarded-For` (`--forwarded-allow-ips='*'`), damit das Rate-Limit die echte Client-IP sieht. Deshalb darf nur `frontend` öffentlich erreichbar sein, nie `api` direkt.
- Das Rate-Limit liegt im Speicher des API-Prozesses. Die API darf deshalb nur mit **einer** Instanz laufen, bis das Limit in die Datenbank wandert (siehe offene Fragen in `09-roadmap.md`).

## Lokal mit Docker

```sh
cp .env.example .env              # Passwort setzen, OO_COOKIE_SECURE=false für http://localhost
docker compose up --build
# → http://localhost:8080
```

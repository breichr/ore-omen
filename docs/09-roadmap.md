# 09 – Implementierungs-Roadmap

Jeder Meilenstein ist für sich spielbar und deploybar. **Erst abschließen, dann den nächsten beginnen.** Innerhalb eines Meilensteins in der angegebenen Reihenfolge arbeiten.

Schätzungen sind Abende à ca. 3 h mit Claude Code, als grobe Orientierung.

| Meilenstein | Ergebnis | Aufwand |
|---|---|---|
| M0 Fundament | Einloggen, Charakter anlegen, installierbare PWA | 3–4 Abende |
| M1 Siedlung & Zeit | Bauen, produzieren, arbeiten | 4–5 Abende |
| M2 Aufträge & Ruf | Onboarding, Fraktionen, Proben | 5–6 Abende |
| M3 Duelle | Asynchrones PvP mit Protokoll | 4–5 Abende |
| M4 Push | Benachrichtigungen auf dem Handy | 2 Abende |
| M5 Kopfgeld & Verderbnis | Die eigentliche Identität des Spiels | 6–8 Abende |
| M6 Closed Beta | Admin, Telemetrie, Tester | 3–4 Abende |

**Gesamt bis Beta: ca. 27–34 Abende.**

---

## M0 – Fundament

### Aufgaben
- [x] Offene Entscheidungen aus `08-technik.md` klären (Stack, Domain, Zeitzone, Sprache)
- [x] Repo-Struktur anlegen, `tools/duel_sim.py` übernehmen
- [x] `docker-compose.yml` mit `db`, `api`, `worker`, `frontend`
- [x] Backend-Grundgerüst: FastAPI, Settings über Umgebungsvariablen, Healthcheck `/health`
- [x] SQLAlchemy + Alembic, erste Migration: `users`, `characters` (+ `sessions`)
- [x] Auth: Registrierung, Login, Logout, Session-Cookie, Argon2, Rate-Limit
- [x] Charaktererstellung: Name (eindeutig), Klasse, 5 Startpunkte je Attribut + 4 frei verteilbar, 5 Skillpunkte (unverteilt)
- [x] `app/game/constants.py` mit allen Konstanten aus den Docs (auch wenn noch ungenutzt)
- [x] Frontend: SvelteKit, Routing, Login-/Register-Screen, Charaktererstellung, leerer „Hof“-Screen
- [x] PWA: Manifest, Icons, Service Worker mit App-Shell-Cache, Offline-Hinweis
- [x] CI: Tests + Lint bei jedem Push (`.github/workflows/ci.yml`)
- [ ] Deployment auf Coolify – Anleitung in `docs/deploy.md`, hakt der Projektinhaber ab
- [x] Login per Benutzername statt E-Mail, Notfall-Wiederherstellungsschlüssel für Passwort-Reset
- [x] Kleine Landing Page für Gäste statt direktem Login

### Abnahme
Auf dem Handy registrieren, Charakter anlegen, App installieren, schließen, wieder öffnen → noch eingeloggt.

### Prompt für Claude Code
```
Lies CLAUDE.md, docs/00-uebersicht.md, docs/01-welt.md und docs/08-technik.md.
Setze Meilenstein M0 aus docs/09-roadmap.md um. Arbeite die Aufgabenliste der
Reihe nach ab und hake erledigte Punkte in docs/09-roadmap.md ab.
Frag nach, bevor du offene Entscheidungen aus 08-technik.md selbst triffst.
```

---

## M1 – Siedlung & Zeit

### Aufgaben
- [ ] `app/game/buildings.py`: reine Funktionen für Kosten, Bauzeit, Produktion, Lager, geschützter Anteil
- [ ] Unit-Tests mit der Referenztabelle aus `03-siedlung.md` (Holzfällerplatz Stufe 1/3/5/7/10)
- [ ] `content/buildings.yaml` mit allen Gebäuden und Basiswerten
- [ ] Migration: `buildings`, `build_queue`, `resources`, `scheduled_events`
- [ ] Ressourcen mit Lazy-Berechnung (Stand + Rate × Δt, gedeckelt durch Lager)
- [ ] Worker: Schleife mit `FOR UPDATE SKIP LOCKED`, Handler-Registry nach `kind`
- [ ] Bauen: Prüfungen (Haupthaus-Stufe, Ressourcen, Warteschlange, Ausschlussregeln), Abbruch mit 50 % Erstattung
- [ ] Arbeiten: 3–5 einfache Jobs (Holz hacken, Vieh treiben …) als Timer
- [ ] Charakterstufe und Erfahrung, Attributpunkte bei Stufenaufstieg
- [ ] Frontend: Hof-Screen (Gebäudeliste, Stufen, Ausbau-Button mit Kosten und Zeit), Lageranzeige, Arbeitsliste, lokaler Countdown
- [ ] Integrationstest: Bau starten → Zeit vorspulen → Worker verarbeitet → Stufe erhöht

### Abnahme
Holzfällerplatz auf Stufe 3 ausbauen. Produktion und Bauzeit stimmen exakt mit der Referenztabelle. Lager läuft voll und stoppt. Kapelle und Erzschrein schließen sich aus.

### Prompt
```
Lies CLAUDE.md und docs/03-siedlung.md. Setze M1 aus docs/09-roadmap.md um.
Beginne mit app/game/buildings.py und den Unit-Tests gegen die Referenztabelle,
bevor du DB oder API anfasst. Zeit im Worker muss für Tests injizierbar sein.
```

---

## M2 – Aufträge & Ruf

### Aufgaben
- [ ] `app/game/reputation.py`: Rufstufen, Beziehungsmatrix, Treueschwur, Deckel (Orden bei Verderbnis ≥ 50, Aschenbande-Voraussetzungen)
- [ ] Tests: Beispiel „+40 Aschenbande → −20/−20/−4“
- [ ] `app/game/quests.py`: Proben (W20 + Attribut + Skill ≥ Schwierigkeit), Erfolgschance berechnen, Effekte anwenden
- [ ] JSON-Schema für Aufträge, Validierung aller Dateien in `content/quests/` in der CI
- [ ] Migration: `reputation`, `oaths`, `quest_instances`, `items`
- [ ] Auftragsablauf: starten → Timer → Ereignis → Wahl → Ausgang, Seed pro Instanz
- [ ] Tagesarbeiten: tägliches Würfeln um 04:00 (`daily_reset`-Ereignis)
- [ ] Inhalte: Onboarding „Der letzte Zug“ (vorher mit Projektinhaber ausformulieren), je Fraktion 3 Tagesarbeiten + 1 Fraktionsauftrag aus `07-auftraege.md`
- [ ] Reisen zwischen Regionen als Timer
- [ ] Frontend: Auftragsliste, Ereignis-Screen mit Optionen und Prozentanzeige, Fraktions-Screen mit Rufbalken

### Abnahme
Neuer Spieler kommt in ca. 30 Minuten durch das Onboarding. Rufnebenwirkungen stimmen mit der Matrix. Neuladen während einer Probe ändert das Ergebnis nicht.

### Prompt
```
Lies CLAUDE.md, docs/02-fraktionen.md und docs/07-auftraege.md. Setze M2 um.
Starte mit reputation.py und quests.py samt Tests, dann das JSON-Schema.
Für das Onboarding erst einen Textentwurf vorlegen und auf Freigabe warten.
```

---

## M3 – Duelle

### Aufgaben
- [ ] `app/game/duel.py` als Port von `tools/duel_sim.py` (Logik identisch, sauber typisiert, ohne Konsolenausgabe)
- [ ] Vergleichstest: 1.000 Duelle mit festen Seeds gegen den Simulator, Ergebnisse müssen identisch sein
- [ ] Balancing-Test in der CI: Klassenmatrix mit 2.000 Duellen je Paar, jede Klasse im Korridor 45–55 %
- [ ] Duellwerte aus Attributen, Skills und Ausrüstung berechnen
- [ ] Migration: `duels`, `duel_tactics`, `character_skills`
- [ ] Gegnerliste in Stufenrange (80–125 %), keine Verletzten, keine in der Stadt ohne Zustimmung
- [ ] Beute, Erfahrung, Verletzung (2 h)
- [ ] Übungsduell gegen NPCs (`content/enemies.yaml`)
- [ ] Frontend: Taktik-Screen (Gewichtungs-Regler), Angriffsplanung (6 Züge), Protokoll mit Zeilenanimation und aufklappbaren Trefferchancen

### Abnahme
Duell zwischen zwei Testaccounts. Protokoll ist nachvollziehbar. Balancing-Test in der CI ist grün.

### Prompt
```
Lies CLAUDE.md und docs/04-duelle.md. Portiere tools/duel_sim.py nach
backend/app/game/duel.py für M3. Schreib zuerst den Vergleichstest gegen den
Simulator, dann den Port. Ändere keine Balancing-Werte ohne Rückfrage.
```

---

## M4 – Push

### Aufgaben
- [ ] VAPID-Schlüssel, `push_subscriptions`, Subscribe/Unsubscribe
- [ ] Versand aus dem Worker: Bau fertig, Auftrag fertig, Arbeit fertig, angegriffen worden
- [ ] Einstellungen pro Benachrichtigungsart, Ruhezeiten (Standard 22–7 Uhr)
- [ ] Push-Opt-in erst nach dem ersten abgeschlossenen Timer
- [ ] Deep Links: Tap auf Push öffnet den passenden Screen

### Abnahme
Push kommt auf Android (Chrome) und iOS (installierte PWA, ab iOS 16.4) an.

---

## M5 – Kopfgeld & Verderbnis

### Aufgaben – Kopfgeld
- [ ] Überfälle auf Siedlungen: Beute unter Berücksichtigung von geschütztem Lager, Hundezwinger, Palisade; Brandschaden
- [ ] `app/game/bounty.py`: Entstehung, Stufen, Einlösen (100 %/50 %), Festnahme, Abbau 5 %/Tag, Freikaufen, Tilgen
- [ ] Missbrauchsschutz laut `05-kopfgeld.md` inkl. Logging auffälliger Paare
- [ ] Kopfgeldjäger-Bonus im Duell aktivieren
- [ ] Steckbriefbrett, Sperren für „Gefährlich“ und „Berüchtigt“

### Aufgaben – Verderbnis
- [ ] `app/game/corruption.py`: Stufen, Kräfte, Quellen, Senken (Zehntel intern)
- [ ] Tägliches Ereignis `corruption_daily`: Kapelle, natürlicher Abbau, „Das Erz flüstert“, Orden-Kopfgeld
- [ ] Gebäude Kapelle, Erzschrein, Flüsterbrunnen, Totenacker mit Wirkung
- [ ] Beichte, Prediger-Segen an andere Spieler
- [ ] Flüster-Ereignisse mit Auto-Auswahl nach 12 h, Inhalte in `content/whispers/`
- [ ] Schwarzerz-Kugeln und Dunkler Blick im Duell
- [ ] Verderbnis-Langzeitsimulation im Simulator ergänzen (siehe TODO in `06-verderbnis.md`)

### Abnahme
Ein Testcharakter geht von Rein bis Besessen und zurück. Kopfgelder entstehen und werden eingelöst. Selbst-Einlösen und Bandenfreunde werden abgewiesen.

---

## M6 – Closed Beta

### Aufgaben
- [ ] Admin-Bereich: Spielersuche, Zustand ansehen, Ereignis-Log, Konstanten live einsehen
- [ ] Telemetrie (anonym): Session-Länge, Siegquoten pro Klasse, Verderbnisverteilung, Abbruchstelle im Onboarding
- [ ] Fehlertracking (z. B. selbstgehostetes GlitchTip)
- [ ] Datenschutzerklärung, Impressum, Nutzungsbedingungen (ein Account pro Person)
- [ ] Backup-Restore einmal testweise durchspielen
- [ ] Feedback-Knopf in der App
- [ ] 20–50 Tester einladen

### Abnahme
Zwei Wochen Beta ohne Datenverlust. Mindestens 60 % der Tester schließen das Onboarding ab.

---

## Nach der Beta

**Phase 2**: Serverweiter Fraktionseinfluss · Blutmond · Banden mit Saloon und Versteck · „Die Tiefe ruft“ · Tiefe Ader als Stockwerk-Dungeon

**Phase 3**: Minenschächte und wöchentliche Bandenkämpfe · Questreihen *Fracht nach Osten* und *Was im Berg schläft* · Nebenklassen ab Stufe 25

---

## Arbeitsweise mit Claude Code

- Pro Sitzung **einen** Meilenstein-Abschnitt angehen, nicht mehrere
- Am Ende jeder Sitzung: Tests grün, erledigte Punkte abhaken, offene Fragen unten in dieser Datei notieren
- Spiellogik immer zuerst als reine Funktion mit Test, dann DB, dann API, dann UI
- Neue Regeln oder Wertänderungen zuerst im passenden Doc, dann im Code

## Offene Fragen

*(hier während der Umsetzung ergänzen)*

- **Überfälle auf Siedlungen** (vor M5 ausarbeiten): Ablauf und Auflösung (Duell? eigene Probe?), Stufenrange, Wirkung von Palisade und Wachturm in Zahlen, Chance auf Brandschaden.
- **Balancing-CI (M3)**: Mit `duel_sim.py --seed 1 -n 2000 klassen` liegt der Kopfgeldjäger bei **42,9 %**, also schon unter dem CI-Korridor 43–57 %. Vor M3 entscheiden: mehr Duelle je Paar (z. B. 10.000), Kopfgeldjäger nachbalancieren oder Korridor für ihn anpassen.
- **Skillpunkte verteilen (M1/M3)**: Neue Charaktere haben 5 unverteilte Skillpunkte. Verteilung und `character_skills` kommen mit der Stufenlogik in M1 oder mit M3. Welcher Meilenstein?
- **Rate-Limit** liegt im Speicher des API-Prozesses (reicht für eine Instanz). Vor horizontaler Skalierung in Postgres verlegen.
- **Notfallschlüssel neu erzeugen**: Derzeit gibt es einen neuen Schlüssel nur über die Wiederherstellung. Soll man ihn auch eingeloggt (mit Passwort) neu erzeugen können, z. B. in einem Einstellungs-Screen?
- **Alt-Konten**: Konten aus der Zeit vor Migration 0002 heißen `user<ID>` und haben keinen Notfallschlüssel. Betrifft nur Testkonten.
- **Onboarding vs. Startzustand**: Der Hof ist nach der Erstellung leer, das Zelt baut der Spieler in M1/M2 selbst (Onboarding-Schritt 3).

# Ore & Omen

Textbasiertes Multiplayer-Browsergame als PWA fürs Smartphone. Weird West im Jahr 1878: die Minenstadt **Hollow Creek**, ein schwarzes Erz, das Macht verleiht und verdirbt, Aufbau + RPG + asynchrones PvP.

## Bevor du etwas baust

1. Lies `docs/00-uebersicht.md` für Vision und Kern-Loop.
2. Lies das Dokument des Systems, an dem du arbeitest (Liste unten).
3. Zahlen und Formeln in den Docs sind **verbindlich**. Wenn du eine Regel ändern musst, ändere zuerst das Doc und sag es.
4. Balancing-Konstanten gehören in **eine** zentrale Konfigurationsdatei (`backend/app/game/constants.py`), nie verstreut im Code.

## Dokumente

| Datei | Inhalt |
|---|---|
| `docs/00-uebersicht.md` | Vision, Zielgruppe, Kern-Loop, Designprinzipien |
| `docs/01-welt.md` | Setting, Regionen, Ressourcen, Klassen, Attribute |
| `docs/02-fraktionen.md` | Vier Fraktionen, Rufstufen, Beziehungsmatrix, Treueschwur |
| `docs/03-siedlung.md` | Gebäude, Ausbauformeln, Lager, Basiswerte |
| `docs/04-duelle.md` | Duellsystem mit allen Formeln (balanciert per Simulator) |
| `docs/05-kopfgeld.md` | Kopfgeld: Entstehung, Steckbriefstufen, Einlösen, Missbrauchsschutz |
| `docs/06-verderbnis.md` | Verderbnis-Skala, Kräfte, Quellen, Senken, „Die Tiefe ruft“ |
| `docs/07-auftraege.md` | Auftragsarten, Proben, Datenformat, Beispielaufträge |
| `docs/08-technik.md` | Architektur, Stack, Datenmodell, Tick-System, Push, Deployment |
| `docs/09-roadmap.md` | Meilensteine mit Abnahmekriterien |
| `tools/duel_sim.py` | Referenzimplementierung + Balancing-Simulator für Duelle |

## Konventionen

- **Sprache**: UI-Texte und Spielinhalte auf Deutsch. Code, Bezeichner, Commits und API auf Englisch.
- **Server ist die Wahrheit**: Jede Spielberechnung (Kämpfe, Proben, Produktion, Timer) läuft serverseitig. Der Client zeigt nur an und sendet Absichten.
- **Deterministisch**: Zufall läuft über einen gespeicherten Seed pro Ereignis, damit Kämpfe und Proben nachvollziehbar und testbar sind.
- **Zeit**: Alle Zeitpunkte in UTC speichern, im Client lokal anzeigen.
- **Inhalte als Daten**: Aufträge, Gebäude-Basiswerte und Items liegen als JSON/YAML in `content/`, nicht im Code.
- **Tests**: Jede Formel aus den Docs bekommt einen Unit-Test mit einem Beispielwert aus dem jeweiligen Doc.
- **Duell-Engine**: Muss dieselben Ergebnisse liefern wie `tools/duel_sim.py` bei gleichem Seed-Verhalten der Mechanik. Der Simulator ist die Referenz.

## Offene Entscheidungen

Stehen in `docs/08-technik.md` unter „Offen“. Nicht eigenmächtig entscheiden, sondern nachfragen.

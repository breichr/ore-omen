# 07 – Aufträge

## Arten

| Art | Code | Wiederholbar | Ruf | Umfang |
|---|---|---|---|---|
| Tagesarbeit | `daily` | 3 pro Fraktion pro Tag | +10 bis +20 | 0–1 Entscheidung, 15 min–2 h |
| Fraktionsauftrag | `faction` | einmalig | +30 bis +50 | 1–3 Entscheidungen, an Rufstufe gebunden |
| Questreihe | `chain` | einmalig | variabel | mehrtägig, schaltet Regionen/Gebäude/Titel frei |

Tagesarbeiten werden täglich um 04:00 Serverzeit neu gewürfelt:

- Jede Fraktion bietet pro Tag **3 Tagesarbeiten** aus ihrem Pool an; jede kann einmal pro Tag erledigt werden.
- Kein Mindestruf. Die Hüter-Tagesarbeiten spielen außerhalb der Schlucht.
- Das Angebot wird aus Spieltag (Wechsel 04:00 Europe/Vienna) und Charakter abgeleitet (Seed), es braucht dafür kein eigenes Ereignis.

**Eine Tätigkeit zur Zeit**: Arbeit, Auftrag (Unterwegs-Timer) und Reise schließen sich gegenseitig aus. Das Ereignis am Ziel (die Wahl) blockiert nichts.

## Ablauf eines Auftrags

1. **Einstieg** – 3–5 Sätze
2. **Unterwegs** – Timer, Push bei Ankunft
3. **Ereignis** – Text + 2–3 Optionen, optional mit Probe
4. **Ausgang** – Belohnung, Ruf, Verderbnis, Items, Folgeaufträge

Jeder Schritt muss auf einen Smartphone-Bildschirm passen.

## Proben

```
Erfolg, wenn W20 + Attribut + Skillpunkte ≥ Schwierigkeit

leicht 15 · mittel 22 · schwer 28 · tödlich 35
```

- Die Erfolgschance steht an jeder Option: „Überreden – 65 %“
- Misserfolg führt immer zu einem eigenen, schlechteren Ausgang, nie zu „nichts passiert“
- Proben verwenden den Seed des Auftrags (wiederholbar, kein Neuladen-Exploit)
- Proben laufen nur auf Attribute + einen Skill dieses Attributs (siehe `01-welt.md`), nie auf Duellwerte direkt. Im JSON: `"check": {"attribute": "intellect", "skill": "instinct", "difficulty": 15}`; `skill` ist optional

## Datenformat

Aufträge liegen als JSON in `content/quests/<fraktion>/<id>.json`. Die Engine berechnet Rufverluste bei anderen Fraktionen automatisch aus der Beziehungsmatrix (`02-fraktionen.md`).

```json
{
  "id": "orden_glocke",
  "type": "faction",
  "faction": "order",
  "min_reputation": 200,
  "region": "kiefernhang",
  "duration_min": 45,
  "title": "Die Glocke von San Isidro",
  "intro": "Jede Nacht um drei läutet die Glocke der verlassenen Kapelle am Fluss. Es gibt dort seit zehn Jahren kein Seil mehr.",
  "event": "Du steigst den Turm hinauf. Am Glockenschwengel hängt ein Mann in Priesterrobe und zieht, ohne hochzusehen.",
  "options": [
    {
      "label": "Ihn segnen und erlösen",
      "check": { "attribute": "charisma", "difficulty": 22 },
      "success": {
        "text": "Er lässt das Seil los, das nicht da ist. Dann ist er fort.",
        "effects": { "reputation": { "order": 40 }, "items": ["bell_shard"] }
      },
      "failure": {
        "text": "Er dreht den Kopf. Viel zu weit.",
        "effects": { "combat": "revenant_1" }
      }
    },
    {
      "label": "Das Seil durchschneiden",
      "effects": { "reputation": { "order": 20 } },
      "text": "Die Glocke verstummt. Der Mann zerfällt zu Asche."
    },
    {
      "label": "Die Glocke abnehmen und verkaufen",
      "effects": {
        "dollars": 300,
        "reputation": { "order": -40 },
        "corruption": 3,
        "status": { "whispers_days": 3 }
      },
      "text": "Mae zahlt ohne Fragen. Auf dem Heimweg hörst du Schritte hinter dir."
    }
  ]
}
```

### Effekt-Schlüssel

| Schlüssel | Typ | Bedeutung |
|---|---|---|
| `dollars` | int | Dollar (+/−) |
| `resources` | `{name: int}` | Ressourcen |
| `xp` | int | Erfahrung |
| `reputation` | `{faction: int}` | Direkter Ruf |
| `corruption` | number | Verderbnis (+/−) |
| `bounty` | `{issuer, amount}` | Kopfgeld erzeugen |
| `items` | `[item_id]` | Gegenstände |
| `combat` | `enemy_id` | Kampf gegen NPC (Duell-Engine) |
| `status` | `{name: value}` | Zeitlich begrenzte Zustände |
| `unlock` | `[id]` | Regionen, Aufträge, Rezepte freischalten |
| `server_flag` | `{name: value}` | Serverweite Auswirkungen (z. B. Blutmond stärker) |
| `next` | `quest_id` | Folgeauftrag |

Option-Bedingungen (optional): `requires` mit `class`, `min_corruption`, `max_corruption`, `item`, `reputation`, `dollars`.

Zusätzliche Felder (JSON-Schema: `content/quests/schema.json`, in der CI geprüft):

| Feld | Bedeutung |
|---|---|
| `after` | Auftrag erst verfügbar, wenn dieser Auftrag abgeschlossen ist (Questreihen) |
| `task` | Aufgabe statt Ereignis: `{"job": code}` oder `{"build": code}`; wird nach `duration_min` erledigt |
| `effects` + `text` auf oberster Ebene | Auftrag ohne Ereignis: Ausgang direkt bei Ankunft |
| `check.skill` | optionaler Skill zum Attribut; `difficulty` als Zahl oder `easy`/`medium`/`hard`/`deadly` |

**Effekte ohne fertiges System** (`combat`, `bounty`, `status`, `server_flag`) werden gespeichert und angezeigt; ihre Wirkung kommt mit dem jeweiligen Meilenstein. Bis M3 gilt ein `combat` als verloren. Verderbnis wird gespeichert und wirkt ab M5. Gegenstände landen als Inventar in `items` (`content/items.yaml`).

**Fraktionsaufträge in M2**: *Der stille Schacht* und *Die Glocke von San Isidro*. *Der Drei-Uhr-Zug* (mehrere Spieler, fester Termin) und *Die Karte, die sich bewegt* (drei Abende) kommen, sobald die Mechaniken dafür stehen.

## Beispielaufträge

### Kompanie – Tagesarbeit: Lohngeld nach Kiefernhang · 1 h
> Die Kiste ist schwerer, als sie sein sollte. Auf halber Strecke liegt ein Baumstamm quer über dem Weg. Zu sauber gefällt für einen Sturm.

- Weiterfahren und kämpfen → Kampf gegen `bandit_1`; Sieg: +15 Kompanie, 60 $
- Umweg durch den Wald (Verstand, leicht) → Erfolg: +15 Kompanie, 60 $ · Fehlschlag: +30 min, 54 $
- Kiste öffnen → +50 $ extra; Probe Charisma mittel, bei Fehlschlag −20 Kompanie

### Kompanie – Fraktionsauftrag: Der stille Schacht · ab Geschätzt
> Schacht 7 meldet sich seit zwei Tagen nicht. Vale will einen Bericht, „bevor die Zeitungen einen schreiben“. Unten findest du die Schicht: acht Männer, stehend, mit offenen Augen. Aus den Wänden wachsen schwarze Kristalle, wo gestern noch Fels war.

- Bericht: Gasunfall → +40 Kompanie, +150 $, −20 Orden (direkt)
- Die Wahrheit berichten → +10 Kompanie, +20 Orden, +20 Hüter, Folgeauftrag `kompanie_vales_gedaechtnis`
- Kristalle mitnehmen → +8 Schwarzerz, +6 Verderbnis
- *Zusatzoption* Die Wände untersuchen (Verstand, schwer) → Freischaltung `hueter_hinweis_schacht7`

### Orden – Tagesarbeit: Salz für die Höfe · 30 min
Kein Ereignis. +10 Orden, +1 Salz.

### Orden – Fraktionsauftrag: Die Glocke von San Isidro · ab Bekannt
Siehe Datenformat oben.

### Aschenbande – Tagesarbeit: Erz über den Salzsee · 2 h
Spieler ist während des Timers für Gesuchte und Kopfgeldjäger auf der Karte als Ziel sichtbar und kann abgefangen werden (Duell). Erfolg: +20 Aschenbande, 80 $.

### Aschenbande – Fraktionsauftrag: Der Drei-Uhr-Zug · ab Geschätzt, 1–3 Spieler
> Mae breitet eine Karte auf dem Tisch aus. „Donnerstag, drei Uhr, der Zahlungszug der Kompanie. Ich brauche Leute, die nicht zittern.“

**Planungsphase** (asynchron bis zum festen Termin): Jeder Teilnehmer wählt eine Rolle mit Probe.
- Sprengen (Stärke, schwer) · Schaffner bestechen (Charisma, mittel) · Aufs Dach, Schloss knacken (Geschick, schwer)

Jede erfolgreiche Rolle senkt die Schwierigkeit des Überfalls um 5 (Basis: tödlich 35). Auflösung zum Termin, Push an alle.

> Im Tresorwagen: Lohngeld. Und ein Sarg mit Kompaniesiegel, der von innen kalt ist.

- Nur das Geld → 600 $ geteilt, +40 Aschenbande, Kopfgeld (Kompanie) für alle
- Den Sarg öffnen → Relikt, +10 Verderbnis für den Öffnenden, startet serverweite Questreihe `chain_fracht_nach_osten`
- Den Sarg dem Orden bringen → −20 Aschenbande, +50 Orden, Status `mae_vergisst_nicht`

### Hüter – Tagesarbeit: Fundstücke aus der Tiefe
Beim Schürfen in der Tiefen Ader 10 % Chance auf ein Fundstück. Bei Ada abliefern: +15 Hüter, 20 % Chance auf einen Hinweis.

### Hüter – Fraktionsauftrag: Die Karte, die sich bewegt · ab Bekannt, 3 Tage
> Ada gibt dir eine Karte der Tiefen Ader. „Schau sie dir jeden Abend an. Dann sag mir, was sich verändert hat.“

An drei Abenden (ab 20:00 Ortszeit des Spielers) je eine Auswahl aus drei Veränderungen. Verstand-Probe (leicht/mittel/schwer an Tag 1/2/3) markiert bei Erfolg die richtige Option.
- 3/3 richtig → +50 Hüter, Freischaltung eines neuen Bereichs der Tiefen Ader
- 1–2 richtig → +25 Hüter
- Karte an die Kompanie verkaufen → +30 Kompanie, 250 $, −60 Hüter, `server_flag: blood_moon_stronger`

## Arbeiten

Einfache Timer-Tätigkeiten ohne Entscheidung und ohne Probe. Liegen als Daten in `content/jobs.yaml`.

| Job | Code | Dauer | Ertrag | XP |
|---|---|---|---|---|
| Holz hacken | `chop_wood` | 15 min | 25 Holz | 10 |
| Vieh treiben | `drive_cattle` | 30 min | 20 Vieh, 15 $ | 20 |
| Kisten am Bahnhof schleppen | `haul_crates` | 1 h | 50 $ | 35 |
| Erz sortieren | `sort_ore` | 2 h | 40 Eisen, 30 $ | 60 |

- Immer nur **ein** Job gleichzeitig. Abbruch: kein Ertrag, keine XP.
- Ertrag (nicht XP) steigt um **10 % pro Charakterstufe über 1**: `Ertrag × (1 + 0,1 × (Stufe − 1))`, gerundet.
- Ressourcen-Ertrag ist durch das Lager gedeckelt (`03-siedlung.md`, „Lagergrenze“).

## Einstieg: Questreihe „Der letzte Zug“ (Onboarding)

Führt in ca. 30 Minuten durch alle Grundsysteme. Texte freigegeben, liegen in `content/quests/onboarding/`.

1. **Ankunft** – Mantel mitnehmen (Gegenstand „Fremder Mantel“) oder hängen lassen
2. **Erste Arbeit** – Kisten schleppen, im Onboarding **1 min** (Ertrag wie der Job)
3. **Ein Dach** – Zelt (Haupthaus Stufe 1) bauen, im Onboarding **1 min**, Kosten wie normal
4. **Der Mann aus dem Abteil** – erste Probe (Charisma + Überreden, leicht), Alternativen: Whiskey (5 $) oder Mantel zeigen
5. **Übungsduell** gegen den Hilfssheriff – kommt mit M3
6. **Die Stadt ruft** – eine Fraktion wählen, +20 Ruf dort (Nebenwirkungen sichtbar)

Die Verkürzungen gelten nur innerhalb des Onboardings, sonst gelten die normalen Werte.

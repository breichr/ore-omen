# 07 – Aufträge

## Arten

| Art | Code | Wiederholbar | Ruf | Umfang |
|---|---|---|---|---|
| Tagesarbeit | `daily` | 3 pro Fraktion pro Tag | +10 bis +20 | 0–1 Entscheidung, 15 min–2 h |
| Fraktionsauftrag | `faction` | einmalig | +30 bis +50 | 1–3 Entscheidungen, an Rufstufe gebunden |
| Questreihe | `chain` | einmalig | variabel | mehrtägig, schaltet Regionen/Gebäude/Titel frei |

Tagesarbeiten werden täglich um 04:00 Serverzeit neu gewürfelt.

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

Option-Bedingungen (optional): `requires` mit `class`, `min_corruption`, `max_corruption`, `item`, `reputation`.

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

## Einstieg: Questreihe „Der letzte Zug“ (Onboarding)

Führt in ca. 30 Minuten durch alle Grundsysteme. Muss vor Meilenstein M2 ausgearbeitet werden.

1. Ankunft, der Schaffner ist verschwunden → erste Entscheidung
2. Erste Arbeit (15 min Timer, danach 1 min für neue Spieler)
3. Zelt aufbauen → erstes Gebäude (Haupthaus Stufe 1)
4. Nach dem Mann aus dem Abteil fragen → erste Probe
5. Übungsduell gegen den Hilfssheriff → Duelltaktik kennenlernen
6. Die erste Fraktion ruft → Rufsystem

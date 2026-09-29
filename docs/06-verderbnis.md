# 06 – Verderbnis

Wert von **0 bis 100** pro Charakter. Kein reiner Malus, sondern ein zweiter Fortschrittsweg: mehr Macht, aber ein härteres und einsameres Spiel.

Intern als Ganzzahl in Zehnteln speichern (0–1000), weil manche Quellen 0,5 geben. Damit ist auch die Kapellenformel `1 + Stufe ÷ 2` exakt (Stufe 3 → −2,5 = −25 Zehntel).

## Stufen

| Verderbnis | Stufe | Code | Kraft | Preis |
|---|---|---|---|---|
| 0–24 | Rein | `pure` | – | – |
| 25–49 | Gezeichnet | `marked` | *Erzsinn*: +25 % Schwarzerz beim Schürfen | Händler +10 %, Kapellen-Heilung halbiert |
| 50–74 | Verdorben | `tainted` | *Dunkler Blick* (Duell, siehe `04-duelle.md`) | Keine Heilung in Kirchen, Prediger +20 % Schaden gegen dich, nächtliche Kreaturenangriffe auf die Siedlung, Orden-Ruf max. Neutral |
| 75–99 | Besessen | `possessed` | *Schattenschritt*: erster Schuss gegen dich −20 % (siehe `04-duelle.md`) | Orden-Kopfgeld läuft, Charisma −3, tägliche Flüster-Ereignisse |
| 100 | Verloren | `lost` | – | „Die Tiefe ruft“ |

Kräfte gelten kumulativ (ein Besessener hat Erzsinn, Dunklen Blick und Schattenschritt).

**Sichtbarkeit**: Ab *Verdorben* ist die Stufe für alle sichtbar. Darunter nur mit Wachturm-Aufklärung oder für Kopfgeldjäger.

## Quellen

| Quelle | Verderbnis |
|---|---|
| Schwarzerz-Kugel, pro Schuss | +1 (Aschenfürst: +0,5) |
| Erzschrein-Aktivierung | +5 |
| Flüsterbrunnen-Nutzung | +3 |
| Kopfgeld bei der Aschenbande tilgen | +10 |
| **Das Erz flüstert**: mehr als 50 Schwarzerz im Lager | +1 pro Tag |
| Auftragsentscheidungen | laut Auftrag |

## Senken

| Senke | Verderbnis | Bedingung |
|---|---|---|
| Kapelle | −(1 + Stufe ÷ 2) pro Tag | nicht mit Erzschrein kombinierbar |
| Segen eines Prediger-Spielers | −5 | 1× pro Tag pro Empfänger |
| Beichte (Stille Mission) | −15 | Kosten `200 $ × 2^(Beichten diese Woche)`; Orden *Geschätzt*: −25 % |
| Reinigungsquests | −10 bis −25 | laut Auftrag |
| Hüter-Ritual | −25 | Ehrenrang Hüter, 1× pro Woche |
| Natürlicher Abbau | −1 pro Tag | nur solange Verderbnis < 25 |

## Balancing-Ziel

Ein Duell mit Erzkugeln kostet etwa +6. Eine Kapelle Stufe 10 nimmt −6 pro Tag. Wer den Erzschrein wählt, verzichtet auf die Kapelle und muss teurere Wege gehen. Ergebnis: Erz-Builds sind stärker, aber teurer im Unterhalt – nicht dominant.

TODO: Verderbnis in `tools/duel_sim.py` als Langzeitsimulation abbilden (Wochen-Verlauf eines Erz-Builds vs. reinen Builds).

## Flüster-Ereignisse

Ab *Besessen* einmal täglich zu zufälliger Zeit (Push). Kurzer Text, 2 Entscheidungen. Liegen als Inhalte in `content/whispers/`.

```
Du wachst mit Erde unter den Fingernägeln auf.
Neben deinem Bett liegt ein Beutel Schwarzerz, den du nicht kennst.

→ Behalten            (+3 Schwarzerz, +4 Verderbnis)
→ In den Fluss werfen (−2 Verderbnis)
```

Unbeantwortete Ereignisse wählen nach 12 h automatisch die *schlechtere* Option.

## „Die Tiefe ruft“ (Verderbnis 100)

1. Charakter verschwindet für **24 h** in der Tiefen Ader. Keine Aktionen möglich, Produktion läuft weiter.
2. Er wird zum **Wiedergänger-Boss** mit seinen eigenen Duellwerten ×1,5 und Leben ×3.
3. Andere Spieler können ihn jagen (Kampf wie Duell, aber mehrere Jäger nacheinander, Leben bleibt zwischen Kämpfen erhalten).
4. Wer den letzten Treffer setzt: Schwarzerz (10 × Stufe des Verlorenen) und ein seltenes Relikt.
5. Nach 24 h oder Niederlage: Rückkehr mit **Verderbnis 60** und einer zufälligen permanenten **Narbe**.
6. Serverweiter Push: „Silas ist der Tiefe verfallen.“

Narben (Beispiele, eine pro Rückkehr, stapelbar bis 3):

| Narbe | Bonus | Malus |
|---|---|---|
| Schwarze Adern | +1 Instinkt | Kapellen wirken 20 % schwächer |
| Kaltes Blut | +1 Nerven | Händler +5 % |
| Erzlunge | +10 % Schwarzerz beim Schürfen | −4 Max-Leben |

## Verbindungen

- **Duelle**: Erzkugeln, Dunkler Blick, Schattenschritt, Prediger-Bonus
- **Kopfgeld**: Orden-Kopfgeld ab 75, Tilgung kostet Verderbnis
- **Siedlung**: Kapelle vs. Erzschrein, Totenacker, Flüsterbrunnen
- **Fraktionen**: Orden-Deckel ab 50, Aschenbande-Voraussetzungen ab 25/50
- **Blutmond**: verdorbene Siedlungen werden bevorzugt angegriffen; Besessene können Kreaturen 1× pro Blutmond auf einen Nachbarn lenken

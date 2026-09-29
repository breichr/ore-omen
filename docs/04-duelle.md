# 04 – Duellsystem

Duelle sind **asynchron**: Der Angreifer legt seine Taktik fest, der Verteidiger kämpft mit seiner hinterlegten Standardtaktik. Der Server berechnet das Duell sofort, beide erhalten ein Textprotokoll.

Die Referenzimplementierung ist `tools/duel_sim.py` (Stand v5: v4 + Schattenschritt; die Balancing-Tabelle ist unverändert, weil sie ohne Verderbnis läuft). Alle Werte hier sind per Simulation mit je 5.000–10.000 Duellen geprüft.

## Werte

```
Leben = 40 + 4 × Zähigkeit            (80 bei Zähigkeit 10)
```

## Ablauf

1. **Standoff**: `Reflexe + 2 × Nerven + W20`. Höherer Wert schießt zuerst. Gleichstand: höhere Reflexe, dann Zufall.
2. **Sechs Züge pro Seite**, abwechselnd (eine Trommel).
3. **Ende**: bei Leben ≤ 0 (bewusstlos, nicht tot) oder nach 12 Zügen. Dann gewinnt der höhere Anteil `Leben / Max-Leben`. Exakter Gleichstand = Remis.

## Zielzonen und Bewegungen

Jeder Schuss hat ein **Ziel**, der Beschossene eine **Bewegung**.

| Ziel | Schaden | Zielmodifikator | Gekontert durch |
|---|---|---|---|
| Kopf | 30 | −15 % | Ducken |
| Körper | 20 | ±0 | Seitsprung |
| Beine | 15 | +10 % | Springen |

Ein Beintreffer gibt **+15 %** auf den nächsten Schuss gegen den Getroffenen (einmalig).

## Trefferformel

```
Treffer % = 50
          + 3 × (Zielen − Reflexe_Gegner)
          + Zielmodifikator
          + (Kopf: + max(0, Nerven_Schütze − 10) × 1)
          − 40, wenn die Bewegung das Ziel kontert
          + 15, wenn Bein-Debuff aktiv
          − 25, wenn Staubwolke auf dem Schützen liegt
          − 20 beim ersten Schuss gegen einen Besessenen (Schattenschritt)
          + Fähigkeits-/Kopfgeld-Modifikatoren
begrenzt auf 10 … 90

Schaden   = Zonenschaden × Waffenfaktor
          × 1,25 bei Schwarzerz-Kugeln
          × 1,20 wenn Schütze Prediger und Ziel Verderbnis ≥ 50
          × 0,70 beim ersten Treffer gegen einen Prediger (Segen)
```

## Taktik

- **Angreifer** kann alle 6 Züge einzeln planen (Ziel + Bewegung) oder Gewichtungen nutzen.
- **Verteidiger** hinterlegt Gewichtungen, z. B. Ziel 40/30/30, Bewegung 33/33/34. Der Server würfelt pro Zug danach.
- **Standardgewichtung** für neue Spieler: alles gleichverteilt (⅓). Nicht 50 % Körper – das erzeugt sofort eine ausnutzbare Meta.

## Nebenwerte

- **Nerven**
  - zählen im Standoff doppelt
  - senken den Kopfschuss-Malus um 1 % je Punkt über 10
  - unter 30 % Leben: Chance `max(0, 40 − 2 × Nerven) %`, dass Ziel bzw. Bewegung zufällig statt nach Taktik gewählt wird
- **Instinkt**: Bei jedem Schuss, dessen Ziel gekontert würde, Chance `2 % × Instinkt`, die Bewegung zu lesen. Dann wird auf die beste nicht gekonterte Zone umgezielt.

## Klassenfähigkeiten (je 1× pro Duell)

| Klasse | Fähigkeit | Auslöser (automatisch) | Wirkung |
|---|---|---|---|
| Revolverheld | Fächerschuss | Gegner ≤ 50 % Leben oder eigener 6. Zug | 2 Schüsse in einem Zug, je −10 % |
| Prospektor | Staubwolke | Erster eigener Zug, freie Aktion | Nächster gegnerischer Schuss −25 % |
| Quacksalber | Tinktur | Eigenes Leben < 50 % | +20 Leben statt Schuss (max. Max-Leben) |
| Prediger | Segen | Passiv | Erster erhaltener Treffer ×0,7 |
| Kopfgeldjäger | Fährte | Passiv | Wählt Ziel nach bestem Erwartungsschaden gegen die Bewegungsgewichte des Gegners; +10 % Treffer gegen Spieler mit offenem Kopfgeld |

Erwartungsschaden für die Fährte:
```
EV(Zone) = P(Treffer) × Schaden
         + (Beine: P(Treffer) × 0,15 × 20)     // Wert des Bein-Debuffs
P(Treffer) = p_konter × Treffer%(gekontert) + (1 − p_konter) × Treffer%(frei)
```

## Übernatürliches

- **Schwarzerz-Kugeln**: ×1,25 Schaden, +1 Verderbnis pro abgegebenem Schuss (Aschenfürst: +0,5)
- **Dunkler Blick** (Verderbnis ≥ 50): einmal pro Duell garantiert die Bewegung lesen (wie Instinkt, aber sicher). Wird vor Instinkt geprüft.
- **Schattenschritt** (Verderbnis ≥ 75): Der erste Schuss des Gegners gegen den Besessenen hat −20 % Trefferchance (bei Fächerschuss nur der erste der beiden Schüsse). Im Simulator abgebildet, im Spiel ab M5.

## Rahmenregeln

- Angriff nur auf Spieler mit Stufe zwischen **80 % und 125 %** der eigenen
- Nach Niederlage **2 h verletzt**: nicht angreifbar, Arbeiten −50 % Ertrag
- Beute: **10 % des Bargelds** (nicht Bank), plus Erfahrung und Ruf für den Sieger
- Duell verweigern (nur in der Stadt möglich): −5 Ruf bei allen Fraktionen außer Hütern
- Zufall mit gespeichertem Seed pro Duell, Protokoll wird gespeichert und ist wiederholbar

## Balancing-Stand (v4, Simulator)

Siegquote im Schnitt gegen alle anderen Klassen, alle Werte 10:

| Klasse | Siegquote |
|---|---|
| Prediger | 51,3 % |
| Quacksalber | 50,1 % |
| Revolverheld | 47,8 % |
| Prospektor | 46,9 % |
| Kopfgeldjäger | 44,7 % (53–61 % gegen Gesuchte) |

Weitere Kennzahlen:
- K.O.-Quote ca. 40–48 %
- +10 Vorsprung: Zielen 83 %, Reflexe 78 %, Zähigkeit 67 %, Nerven 53 %, Instinkt 51 %
- Reine Ziel- oder Bewegungsstrategien liegen alle zwischen 44 % und 51 %

**Zielkorridor**: Jede Klasse 45–55 % im Schnitt (Designziel). Nach jeder Regeländerung `python tools/duel_sim.py alles` laufen lassen und diese Tabelle aktualisieren.

**CI-Test**: prüft **43–57 %**, weil 2.000 Duelle je Paar Stichprobenrauschen von etwa ±1–2 Prozentpunkten haben. Das Designziel bleibt 45–55 %.

**Bekannter Grenzfall**: Der Kopfgeldjäger liegt mit 44,7 % knapp unter dem Designziel. Das ist gewollt, weil sein Bonus gegen Gesuchte (53–61 %) ihn ausgleicht. Beim nächsten Balancing-Durchgang beobachten.

## Protokoll (Darstellung)

Das Protokoll wird Zeile für Zeile mit ca. 600 ms Verzögerung eingeblendet, mit „Überspringen“-Button.

```
Mittag. Staub weht über die Hauptstraße.
Rosa zieht zuerst.
Rosa zielt auf die Beine. Jack duckt sich. Treffer – 15 Schaden.
Jack zielt auf den Körper. Rosa duckt sich. Daneben.
…
Die Trommeln sind leer. Jack steht noch, Rosa blutet. Jack gewinnt.
```

Zu jeder Zeile ist die Trefferchance per Tap aufklappbar.

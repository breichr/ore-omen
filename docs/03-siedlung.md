# 03 – Siedlung & Ausbau

Jeder Spieler besitzt eine **Parzelle** am Stadtrand, die sich vom Zeltlager zum befestigten Gehöft entwickelt. Gebäude haben Stufen 1–10. Ausbau läuft über Timer.

## Bauwarteschlange

- Anfangs 1 Bauplatz in der Warteschlange, ab Haupthaus Stufe 5 zwei
- Keine Sofortfertigstellung gegen Echtgeld
- Abbruch eines laufenden Baus erstattet 50 % der Kosten

## Grundformeln

`n` = Zielstufe (1–10)

```
Kosten(n)     = Basiskosten × 1,6^(n−1)                                  (je Ressource, gerundet)
Bauzeit(n)    = Basiszeit   × 1,5^(n−1) × (1 − 0,03 × Haupthaus-Stufe)
Produktion(n) = Basisrate   × n × 1,1^(n−1)                               pro Stunde
Lager(n)      = 1000        × 1,3^(n−1)                                   pro Ressource
Geschützt(n)  = 10 % + 4 % × n                                            Anteil des Lagers vor Überfällen
Reparatur     = 25 % der Kosten der aktuellen Stufe
```

Rundung: Kosten und Produktion auf ganze Zahlen, Bauzeit auf ganze Sekunden, jeweils ROUND_HALF_UP (siehe `08-technik.md`, „Rundung“).

**Referenzwerte für Tests** – Holzfällerplatz (Basis 50 Holz, 20 $, 5 min, 20 Holz/h), ohne Haupthaus-Bonus:

| Stufe | Holz | Bauzeit | Produktion/h |
|---|---|---|---|
| 1 | 50 | 5 min | 20 |
| 3 | 128 | 11 min 15 s | 73 |
| 5 | 328 | 25 min 19 s | 146 |
| 7 | 839 | 56 min 57 s | 248 |
| 10 | 3.436 | 3 h 12 min | 472 |

Lager bei Stufe 10: 10.604 pro Ressource. Designziel: Ab mittleren Stufen fasst das Lager etwa einen Tag Produktion, sodass einmal täglich reinschauen reicht.

## Startzustand

- Die Parzelle startet **ohne Gebäude**. Das erste Gebäude ist das Haupthaus Stufe 1 („Zelt“).
- Startressourcen: **200 Holz, 50 Eisen, 150 $**.
- Lager ohne Lagerschuppen: **500 pro Ressource**, geschützter Anteil **10 %**. Mit Lagerschuppen gelten `Lager(n)` und `Geschützt(n)` mit n = Stufe des Lagerschuppens.

## Gebäude

### Kern
| Gebäude | Code | Basiskosten | Basiszeit | Wirkung |
|---|---|---|---|---|
| Haupthaus | `main_house` | 100 Holz, 50 Eisen, 100 $ | 20 min | Max-Stufe aller anderen Gebäude = Haupthaus-Stufe; −3 % Bauzeit pro Stufe; schaltet Bauplätze frei |
| Lagerschuppen | `storehouse` | 80 Holz, 20 Eisen | 8 min | Lagerkapazität, geschützter Anteil |

Anzeigename des Haupthauses je Stufe: 1 **Zelt** · 2–3 **Hütte** · 4–6 **Blockhaus** · 7–9 **Ranchhaus** · 10 **Herrenhaus**.

### Produktion
| Gebäude | Code | Basiskosten | Basiszeit | Produktion (Basisrate/h) |
|---|---|---|---|---|
| Holzfällerplatz | `lumber_yard` | 50 Holz, 20 $ | 5 min | Holz 20 |
| Viehkoppel | `cattle_pen` | 50 Holz, 20 $ | 5 min | Vieh 20 |
| Brennerei | `distillery` | 50 Holz, 20 $ | 5 min | Whiskey 20 |
| Schmiede | `smithy` | 80 Holz, 40 $ | 10 min | Eisen 10; stellt Waffen, Hufeisen, später Silbermunition her |
| Schürfstelle | `dig_site` | 80 Holz, 40 $ | 10 min | Eisen 10, Silber 2; ab Stufe 5: Schwarzerz 0,5 |

### Charakter & Klassen
Basiskosten je 120 Holz, 60 Eisen, 150 $ · Basiszeit 15 min

| Gebäude | Code | Wirkung |
|---|---|---|
| Schießstand | `shooting_range` | Trainingszeit für Duellwerte −5 % pro Stufe |
| Apotheke | `apothecary` | Tinkturen, Heilung nach Kämpfen; Verletzungsdauer −5 % pro Stufe |
| Kapelle | `chapel` | Verderbnis −(1 + Stufe ÷ 2) pro Tag; **schließt Erzschrein aus** |
| Kartenzimmer | `map_room` | Reisezeiten −2 % pro Stufe, bessere Auftragsbelohnungen |

### Verteidigung
Basiskosten je 100 Holz, 80 Eisen · Basiszeit 12 min

| Gebäude | Code | Wirkung |
|---|---|---|
| Palisade | `palisade` | Grundverteidigung gegen Überfälle |
| Wachturm | `watchtower` | Frühwarnung; Angreifer sehen weniger, du siehst mehr; senkt Brandschaden |
| Hundezwinger | `kennel` | Gestohlene Menge −3 % pro Stufe |
| Salzkreis | `salt_circle` | Schutz nur gegen übernatürliche Angriffe (Blutmond) |

### Übernatürlich
Wie Verteidigung, zusätzlich **Schwarzerz = 5 × n** (linear).

| Gebäude | Code | Wirkung |
|---|---|---|
| Erzschrein | `ore_shrine` | Wandelt Schwarzerz in Kräfte; +5 Verderbnis pro Aktivierung; **schließt Kapelle aus** |
| Totenacker | `boneyard` | Gefallene Kreaturen werden Wächter (stark gegen Blutmond und Überfälle); Händler-NPCs +10 % Preise |
| Flüsterbrunnen | `whisper_well` | Zeigt ein Geheimnis eines anderen Spielers (Lager, Taktik); +3 Verderbnis pro Nutzung |

### Gemeinschaft (Bande)
| Gebäude | Code | Wirkung |
|---|---|---|
| Saloon | `saloon` | Bandenchat, Bandenaufträge |
| Bandenversteck | `hideout` | Gemeinsames Lager und Kasse |
| Förderturm | `headframe` | Ausbau eines eroberten Minenschachts, Grundlage der wöchentlichen Kämpfe (Phase 3) |

## Regeln

- **Ausschluss**: Kapelle und Erzschrein nicht gleichzeitig. Bau des einen ist gesperrt, solange das andere steht. Abriss erstattet nichts.
- **Brandschaden**: Ein Angreifer kann statt Beute ein Gebäude beschädigen (−1 Stufe wirksam, bis repariert). Wachturm senkt die Chance.
- **Blutmond**: Ungeschützte Gebäude können über Nacht beschädigt werden. Salzkreis und Totenacker halten dagegen.
- **Produktion** läuft auch, wenn der Spieler offline ist, bis das Lager voll ist.

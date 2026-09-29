# 02 – Fraktionen & Ruf

## Rufskala

Pro Fraktion ein Wert von **−1000 bis +1000**, Start 0.

| Ruf | Stufe | Code |
|---|---|---|
| −1000 bis −600 | Verhasst | `hated` |
| −599 bis −200 | Feindselig | `hostile` |
| −199 bis 199 | Neutral | `neutral` |
| 200 bis 499 | Bekannt | `known` |
| 500 bis 799 | Geschätzt | `respected` |
| 800 bis 999 | Vertraut | `trusted` |
| 1000 | Ehrenrang | `honored` |

Quellen: Tagesarbeiten (+10 bis +20), Fraktionsaufträge (+30 bis +50), Lieferungen, bestimmte Taten (siehe je Fraktion).

## Beziehungsmatrix

Jeder direkte Rufgewinn bei Fraktion X verursacht automatisch Verlust bei anderen Fraktionen, als Prozentsatz des Gewinns. Rufverluste lösen **keine** Gegeneffekte aus.

| Gewinn bei ↓ / Verlust bei → | Kompanie | Orden | Aschenbande | Hüter |
|---|---|---|---|---|
| **Kompanie** | – | −25 % | −50 % | −25 % |
| **Orden** | −25 % | – | −50 % | 0 |
| **Aschenbande** | −50 % | −50 % | – | −10 % |
| **Hüter** | −25 % | 0 | −10 % | – |

Beispiel: +40 Aschenbande → −20 Kompanie, −20 Orden, −4 Hüter.

Aufträge geben nur den direkten Ruf an, die Engine berechnet die Nebenwirkungen.

## Treueschwur

- Ab *Vertraut* bei Kompanie **oder** Aschenbande muss sich der Spieler festlegen, bevor er dort weiter aufsteigen kann.
- Der Schwur sperrt den Ehrenrang der Gegenseite.
- Wechsel möglich, kostet 50 % des aktuellen Rufs bei der verlassenen Fraktion.

## Die Kompanie

*Sitz: Kontor am Bahnhof · Leitfigur: Direktor Cornelius Vale*
Bergbaukonzern. Ordnung, Geld, Gier. Will das Erz ausbeuten und vertuscht, was es anrichtet.

**Ruf durch:** Schwarzerz zum Festpreis abliefern, Karawanen eskortieren, Kopfgelder auf Aschenbande-Mitglieder einlösen

| Stufe | Belohnung |
|---|---|
| Bekannt | Kompanieladen (Dynamit, Grubenlampen, Werkzeug) |
| Geschätzt | Eskortaufträge, Zinsen auf Bankguthaben |
| Vertraut | Anteilsscheine: tägliche Dividende abhängig von der serverweiten Erzförderung |
| Ehrenrang „Aufseher“ | Vertrag für eigenen Förderturm; wer dich überfällt, bekommt doppeltes Kopfgeld |
| Feindselig | Kompanie setzt Kopfgelder aus, Bahnreisen kosten das Dreifache |

## Der Orden vom Letzten Licht

*Sitz: Stille Mission · Leitfigur: Schwester Agatha*
Wanderprediger und Jäger, die das Übernatürliche bekämpfen – mit geweihten Relikten, die selbst nicht ganz geheuer sind.

**Ruf durch:** Kreaturen jagen, Relikte abliefern, Reinigungsquests, Segen spenden, Kopfgelder auf Verderbte einlösen

| Stufe | Belohnung |
|---|---|
| Bekannt | Silbermunition kaufbar |
| Geschätzt | Beichte 25 % günstiger |
| Vertraut | Geweihte Relikte (Ausrüstung mit Bonus gegen Übernatürliches) |
| Ehrenrang „Lichtträger“ | Salzkreis bis Stufe 10, gebührenfreie Kopfgelder auf Verderbte, führt Blutmond-Verteidigung an |
| **Sperre** | Ab Verderbnis ≥ 50 ist der Ruf auf maximal 199 (*Neutral*) gedeckelt |

## Die Aschenbande

*Sitz: Versteck am Rattlesnake Wells, Salzebene · Leitfigur: Mae Holloway, „die Witwe“*
Outlaws, die Schwarzerz schmuggeln und sich bewusst verderben lassen.

**Ruf durch:** Schwarzerz schmuggeln, Kompanie-Karawanen überfallen, offenes Kopfgeld tragen (+1 Ruf pro 100 $ Kopfgeld pro Tag)

| Stufe | Belohnung |
|---|---|
| Bekannt | Hehler: kauft Beute ohne Händleraufschlag |
| Geschätzt | Kopfgeld-Tilgung günstiger |
| Vertraut | Unterschlupf: Berüchtigte können hier Bank und Handel nutzen |
| Ehrenrang „Aschenfürst“ | Eigene Bandenfahne, Hinterhalte auf Karawanenrouten, Erzkugeln kosten nur halbe Verderbnis |
| **Voraussetzung** | *Vertraut* erst ab Verderbnis ≥ 25, Ehrenrang ab ≥ 50 |

## Die Hüter der Schlucht

*Sitz: Die Schlucht · Leitfigur: Ada Crane, Kartenzeichnerin*
Familien, Trapper und frühe Siedler, die lange vor der Eisenbahn im Tal lebten und die alten Warnungen über den Berg aufgeschrieben haben. Neutral, handeln mit Wissen.

**Ruf durch:** Fundstücke und Karten aus der Tiefen Ader abliefern, Wissen tauschen, Kompanie-Sprengungen verhindern. Ruf wächst am langsamsten.

| Stufe | Belohnung |
|---|---|
| Bekannt | Zutritt zur Schlucht |
| Geschätzt | Hinweise auf versteckte Aufträge, Kartenzimmer 20 % schneller |
| Vertraut | Wegekunde: alle Reisezeiten −15 % |
| Ehrenrang „Hüter“ | Endgame-Questreihe *Was im Berg schläft*, wöchentliches Reinigungsritual (−25 Verderbnis) |

## Serverweiter Einfluss (Phase 2)

Wöchentlich (Montag 00:00 Serverzeit) werden alle direkten Rufgewinne pro Fraktion summiert. Die stärkste Fraktion prägt die folgende Woche:

| Dominiert | Effekt |
|---|---|
| Kompanie | Erzpreise −20 %, Blutmond stärker |
| Orden | Blutmond schwächer, Schwarzerz-Handel in der Stadt verboten |
| Aschenbande | Mehr Karawanen, Überfallbeute +20 %, Sheriff-Kopfgelder +50 % |
| Hüter | Neue Bereiche der Tiefen Ader sichtbar |

Push an alle Spieler am Montag mit dem Ergebnis.

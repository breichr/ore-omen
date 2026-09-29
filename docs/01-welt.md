# 01 – Welt, Klassen, Attribute

## Setting

Territorium im Jahr 1878. Die Eisenbahn kam, dann die Mine, dann das Licht. Seit die Bergleute in der **Tiefen Ader** auf einen schwarz schimmernden Erzgang gestoßen sind, bleiben Tote nicht immer liegen, Kompassnadeln drehen sich nachts, und manche Menschen können plötzlich Dinge, die sie nicht können sollten.

## Regionen

| Region | Rolle | PvP |
|---|---|---|
| **Hollow Creek (Stadt)** | Startgebiet, Saloon, Bank, Sheriffbüro, Kompanie-Kontor, Bahnhof | Sichere Zone: keine Überfälle, Duelle nur mit Zustimmung |
| **Kiefernhang** | Ranches, Holzfäller, erste Aufträge, leichte Kreaturen | Duelle erlaubt |
| **Die Tiefe Ader** | Minen-Dungeon, Stockwerk für Stockwerk, mehr Erz und mehr Grauen | Duelle erlaubt |
| **Salzebene** | Offenes Gebiet, Karawanenrouten der Kompanie, Versteck der Aschenbande | Volles PvP inkl. Abfangen |
| **Stille Mission** | Verlassene Kirche, Sitz des Ordens, Endgame-Ereignisse | Duelle erlaubt |
| **Die Schlucht** | Gebiet der Hüter, nur ab Ruf *Bekannt* bei den Hütern | Kein PvP |

Reisen zwischen Regionen kostet Zeit (Timer), Standard 15–60 min.

## Ressourcen

| Ressource | Herkunft | Verwendung |
|---|---|---|
| Dollar ($) | Arbeit, Aufträge, Handel, Beute | Alles |
| Holz | Holzfällerplatz, Arbeit | Bau |
| Eisen | Schürfstelle, Schmiede | Bau, Waffen |
| Vieh | Viehkoppel | Handel, Nahrung |
| Whiskey | Brennerei | Handel, Tinkturen |
| Silber | Schürfstelle (wenig) | Silbermunition gegen Kreaturen |
| Salz | Orden, Handel | Salzkreis |
| Schwarzerz | Tiefe Ader, Schürfstelle ab St. 5 | Übernatürliche Gebäude, Kräfte, Erzkugeln – erzeugt Verderbnis |

## Attribute

Vier Attribute. Bei Charaktererstellung hat jedes Attribut **5**, dazu kommen **4 frei verteilbare Punkte**. Ab Stufe 2 gibt es **2 frei verteilbare Punkte pro Charakterstufe**.

| Attribut | Wirkt auf |
|---|---|
| **Stärke** | Zähigkeit, Tragen, Bauarbeit |
| **Geschick** | Zielen, Reflexe, Schlösser |
| **Verstand** | Instinkt, Handwerk, Kartenkunde |
| **Charisma** | Nerven, Handel, Überreden, Ruf-Boni |

## Skills

Jedes Attribut hat drei Skills. **Die fünf Duellwerte sind Skills** (fett markiert).

| Attribut | Skills |
|---|---|
| Stärke | **Zähigkeit**, Bauen, Tragen |
| Geschick | **Zielen**, **Reflexe**, Fingerfertigkeit |
| Verstand | **Instinkt**, Handwerk, Kartenkunde |
| Charisma | **Nerven**, Handel, Überreden |

- **5 Skillpunkte** bei Charaktererstellung, danach **3 pro Charakterstufe**.
- Ein Skill darf höchstens **Charakterstufe + 2** Punkte haben.

## Duellwerte

```
Duellwert = Skillpunkte + floor(Attribut / 2) + Ausrüstungsbonus
```

Details zum Kampf in `04-duelle.md`. Der Simulator-Referenzwert 10 entspricht grob Charakterstufe 10. Da die Trefferformel nur Differenzen nutzt, bleibt die Balance bei anderen absoluten Werten erhalten. Durch `floor(Attribut / 2)` dominiert Geschick nicht, obwohl es zwei Duellwerte trägt.

## Proben

```
Erfolg, wenn W20 + Attribut + Skillpunkte ≥ Schwierigkeit
```

Proben laufen immer auf ein Attribut und einen seiner Skills, nie direkt auf einen Duellwert. Schwierigkeiten in `07-auftraege.md`.

## Erfahrung und Stufen

```
XP für den Aufstieg von Stufe n auf n+1 = 100 × n^1,5     (gerundet)
```

| Aufstieg | 1→2 | 2→3 | 3→4 | 4→5 | 5→6 | 9→10 |
|---|---|---|---|---|---|---|
| XP | 100 | 283 | 520 | 800 | 1.118 | 2.700 |

- Stufe 10 bei 11.106 XP insgesamt. Vorerst keine Höchststufe.
- Pro Aufstieg: **2 Attributpunkte** und **3 Skillpunkte**, frei verteilbar, jederzeit (auch später).
- Ein Skill darf höchstens **Charakterstufe + 2** Punkte haben.
- Quellen (M1): Arbeiten. Später Aufträge, Duelle.

## Klassen

Wahl bei Charaktererstellung. Ab Stufe 25 zweite Klasse als Nebenklasse (halbe Boni, keine zweite Duellfähigkeit).

| Klasse | Rolle | Duellfähigkeit (1× pro Duell) |
|---|---|---|
| **Revolverheld** | Duellspezialist | *Fächerschuss*: 2 Schüsse in einem Zug, je −10 % |
| **Prospektor** | Erzabbau, Fallen | *Staubwolke*: nächster gegnerischer Schuss −25 % |
| **Quacksalber** | Tinkturen, Heilung, Gifte | *Tinktur*: +20 Leben statt Schuss |
| **Prediger** | Segen, Bannkreise | *Segen*: erster erhaltener Treffer −30 % Schaden |
| **Kopfgeldjäger** | Spuren, Kopfgelder | *Fährte*: sieht Taktik-Gewichtungen des Gegners; +10 % Treffer gegen Gesuchte |

Klassen haben zusätzlich Arbeits- und Auftragsboni (z. B. Prospektor +20 % Schürfertrag, Prediger kann Segen an andere Spieler vergeben).

## Kreaturen (Auswahl)

| Kreatur | Region | Besonderheit |
|---|---|---|
| Staubhund | Kiefernhang | Rudel, schwach einzeln |
| Wiedergänger | Tiefe Ader, Stille Mission | Nur Silber macht vollen Schaden |
| Erzgewachsener | Tiefe Ader ab Stockwerk 3 | Hinterlässt Schwarzerz |
| Der Schaffner | Questreihe | Taucht nur auf, wenn niemand hinsieht |

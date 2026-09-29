# 05 – Kopfgeld

## Entstehung

| Anlass | Kopfgeld | Aussteller |
|---|---|---|
| Überfall auf eine Siedlung | `50 $ × Stufe_Täter + 25 % der Beute`; ×2, wenn Opfer < 90 % der Täterstufe | Sheriff |
| Überfall auf Kompanie-Karawane | `100 $ × Stufe_Täter` | Kompanie |
| Verderbnis ≥ 75 | `20 $ × (Verderbnis − 70)` pro Tag, solange ≥ 75 | Orden |
| Privat | frei wählbar, mind. 100 $; nur gegen Spieler, die den Aussteller in den letzten 7 Tagen überfallen haben | Spieler (Sheriff behält 10 % Gebühr) |

**Duelle erzeugen kein Kopfgeld.**

Mehrere Kopfgelder auf denselben Spieler werden summiert, jeder Aussteller bleibt aber einzeln gespeichert (für Missbrauchsprüfung und Anzeige).

## Steckbrief-Stufen

| Stufe | Ab (Summe) | Folgen |
|---|---|---|
| Gesucht | 1 $ | Steht am Steckbriefbrett im Sheriffbüro |
| Gefährlich | 1.000 $ | Händler in Hollow Creek +20 % |
| Berüchtigt | 5.000 $ | Kein Zugang zu Bank und Stadt; Kopfgeldjäger sehen deine aktuelle Region |

Berüchtigte versorgen sich im Unterschlupf der Aschenbande (ab *Vertraut*).

## Einlösen

- Duell gegen einen Gesuchten gewinnen → Auszahlung
- **Kopfgeldjäger** erhalten 100 %, andere Klassen 50 %. Der nicht ausgezahlte Rest bleibt als Kopfgeld offen.
- **Festnahme** (nur Kopfgeldjäger, vor dem Duell wählbar): Bei Sieg +25 % Prämie, Gesuchter sitzt 2 h im Gefängnis (nicht angreifbar, keine Aktionen außer Chat), Kopfgeld wird vollständig geschlossen.
- Pro Jäger 1 Versuch pro Tag gegen dasselbe Ziel (egal ob Sieg oder Niederlage).
- Ausgezahlt wird anteilig aus den Einzelkopfgeldern, älteste zuerst.

## Abbau

- Kopfgeld sinkt um **5 % pro Tag**, an dem der Spieler keine neue kopfgeldpflichtige Tat begeht
- **Freikaufen** beim Sheriff: 150 % der aktuellen Summe (nicht möglich, wenn Berüchtigt – dann nur über Aschenbande)
- **Tilgen** bei der Aschenbande: Schwarzerz statt Dollar (Kurs im Balancing festlegen, Vorschlag 1 Erz pro 50 $), +10 Verderbnis; ab Ruf *Geschätzt* 25 % günstiger
- Orden-Kopfgeld endet automatisch, wenn Verderbnis unter 75 fällt

## Missbrauchsschutz

- Einlösen nicht durch den Aussteller selbst
- Einlösen nicht durch Mitglieder derselben Bande wie der Gesuchte oder der Aussteller
- Jäger muss in der Duell-Stufenrange liegen (80–125 %)
- Privatkopfgelder erst ab Stufe 10 des Ausstellers
- Auffälligkeiten loggen: dieselben zwei Accounts mehr als 3× in 7 Tagen als Aussteller/Einlöser-Paar

## Kopfgeldjäger-Bonus im Duell

+10 % Treffer gegen Spieler mit offenem Kopfgeld (siehe `04-duelle.md`). Simulator-Stand: hebt die Siegquote von ca. 44 % auf 53–61 % gegen Gesuchte.

## Benachrichtigungen

- Kopfgeldjäger: Push bei neuem Kopfgeld ≥ 500 $ in ihrer Stufenrange (max. 3 pro Tag)
- Gesuchte: Push „Ein Kopfgeldjäger wurde in deiner Region gesichtet“, sobald ein Jäger das Ziel auswählt (vor dem Duell, mit 10 Minuten Vorlauf, in denen die Verteidigungstaktik angepasst werden kann)

## Screen: Steckbriefbrett

Liste, sortiert nach Summe. Pro Eintrag:
```
GESUCHT
Silas Crane · Stufe 18 · Prospektor
Überfall auf die Parzelle Hartley. Überfall auf eine Kompanie-Karawane.
Zuletzt gesehen: Salzebene
1.450 $
```

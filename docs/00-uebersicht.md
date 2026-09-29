# 00 – Übersicht

## Vision

Ein Browsergame für das Smartphone, das man in kurzen Sessions über den Tag verteilt spielt. Keine Grafik, sondern atmosphärischer Text, klare Entscheidungen und Timer, die im Hintergrund laufen. Vorbilder im Rhythmus: The West, Travian, Torn – aber schlanker, erzählerischer und mit einer übernatürlichen Kernmechanik.

**Pitch:** *Grab tief. Bleib menschlich.* Im Territorium um Hollow Creek ist ein schwarzes Erz aufgetaucht, das Menschen Kräfte verleiht und sie dabei langsam zerfrisst. Spieler bauen ihre Parzelle aus, entwickeln ihren Charakter, schließen sich Fraktionen an, duellieren sich und entscheiden ständig: Macht oder Menschlichkeit.

## Plattform

- PWA, installierbar auf dem Homescreen, Mobile-first (360–430 px Breite)
- Desktop funktioniert, ist aber kein Designziel
- Web Push für Timer, Angriffe, Kopfgelder, Events

## Kern-Loop

```
Charakter auf Arbeit/Auftrag schicken (Timer)
        ↓
Ressourcen, Dollar, Erfahrung, Ruf
        ↓
Parzelle ausbauen · Ausrüstung kaufen · Attribute steigern
        ↓
Duelle, Überfälle, Kopfgelder, Fraktionskämpfe
        ↓
Entscheidungen mit Folgen (Ruf, Verderbnis, Kopfgeld)
```

Eine typische Session: 2–5 Minuten. Pro Tag 4–8 Sessions bei aktiven Spielern, 1–2 bei Gelegenheitsspielern. Beide sollen Fortschritt haben.

## Systeme

1. **Charakter**: Klasse, Attribute, Skills, Ausrüstung → `01-welt.md`
2. **Siedlung**: Gebäude mit Stufen 1–10 → `03-siedlung.md`
3. **Duelle**: asynchron, taktisch → `04-duelle.md`
4. **Kopfgeld**: Folgen für Outlaws, Beruf für Jäger → `05-kopfgeld.md`
5. **Verderbnis**: Macht gegen Menschlichkeit → `06-verderbnis.md`
6. **Fraktionen & Ruf**: vier Parteien, die sich gegenseitig ausschließen → `02-fraktionen.md`
7. **Aufträge**: Textereignisse mit Entscheidungen → `07-auftraege.md`

## Designprinzipien

1. **Nie gleichzeitig online sein müssen.** Alles PvP ist asynchron oder zu angekündigten Zeiten.
2. **Jede Zahl erklärt sich.** Erfolgschancen stehen an der Option, Kampfprotokolle zeigen, warum man verloren hat.
3. **Entscheidungen haben Nebenwirkungen.** Ruf bei einer Fraktion kostet Ruf bei einer anderen, Macht kostet Verderbnis.
4. **Kein Pay-to-Win.** Keine gekaufte Beschleunigung von Timern oder Kampfwerten.
5. **Schutz vor Frust.** Stufenrange für Angriffe, Schutzzeiten, geschützter Lageranteil.
6. **Text trägt die Stimmung.** Kurze, konkrete Sätze. Western-Ton mit einem Unterton, dass etwas nicht stimmt.

## Tonalität

- Knapp, bildhaft, kein Purple Prose
- Das Übernatürliche wird angedeutet, nicht erklärt
- Humor ist erlaubt, aber trocken
- Beispiel: *„Die Kiste ist schwerer, als sie sein sollte. Auf halber Strecke liegt ein Baumstamm quer über dem Weg. Zu sauber gefällt für einen Sturm.“*

## Einstieg neuer Spieler

Man kommt mit dem letzten Zug an, der noch fährt. Der Schaffner verschwindet, bevor man aussteigt. Erste Quest: herausfinden, wer im Abteil gegenüber saß, denn niemand in der Stadt hat ihn je gesehen. Die ersten 30 Minuten führen durch Arbeit, ersten Bau, erste Probe und erstes Übungsduell.

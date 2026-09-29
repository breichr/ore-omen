#!/usr/bin/env python3
"""
Ore & Omen – Duell-Simulator
============================

Bildet das Duellsystem ab und simuliert beliebig viele Duelle,
um das Balancing zu prüfen.

Aufrufe:
    python duel_sim.py demo            # ein Duell mit Textprotokoll
    python duel_sim.py match A B       # N Duelle zwischen zwei Builds
    python duel_sim.py klassen         # Klassen-Matrix bei gleichen Werten
    python duel_sim.py sweep           # Einfluss von Wertunterschieden
    python duel_sim.py kopfgeld        # Kopfgeldjäger mit/ohne Kopfgeld am Ziel
    python duel_sim.py alles           # klassen + sweep + zielwahl + kopfgeld

Optionen: -n ANZAHL (Standard 10000), --seed ZAHL

Alle Stellschrauben stehen im Block KONSTANTEN und BUILDS.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# KONSTANTEN
# ---------------------------------------------------------------------------

LEBEN_BASIS = 40             # v2: vorher 100
LEBEN_PRO_ZAEHIGKEIT = 4      # v2: vorher 10
SCHUESSE_PRO_SEITE = 6

TREFFER_BASIS = 50            # %
TREFFER_PRO_PUNKT = 3         # % pro Punkt Zielen − Reflexe
KONTER_MALUS = 40             # % wenn Bewegung das Ziel kontert
TREFFER_MIN, TREFFER_MAX = 10, 90

ZONEN = {
    #          Schaden, Mod %, gekontert durch
    "Kopf":   (30, -15, "Ducken"),
    "Körper": (20,   0, "Seitsprung"),
    "Beine":  (15, +10, "Springen"),   # v3: Schaden 15 (vorher 12)
}
BEWEGUNGEN = ["Ducken", "Seitsprung", "Springen"]
BEIN_DEBUFF = 15              # v3: vorher 10 – Bonus auf den nächsten Schuss gegen Getroffenen

NERVEN_SCHWELLE = 0.30        # Anteil Leben, ab dem Nerven greifen
NERVEN_BASIS = 40             # % Abweichung bei Nerven 0
NERVEN_PRO_PUNKT = 2
NERVEN_STANDOFF_FAKTOR = 2    # v3: Nerven zählen im Standoff doppelt
NERVEN_KOPF_PRO_PUNKT = 1     # v3: Kopfschuss-Malus sinkt um 1 % je Nerven über 10

INSTINKT_PRO_PUNKT = 2        # v3: % Chance pro Punkt, JEDEN gekonterten Schuss umzulenken

SCHWARZERZ_SCHADEN = 1.25     # v2: vorher 1.5
SEGEN_FAKTOR = 0.7            # v2: erster Treffer −30 % (vorher halbiert)
VERDERBNIS_DUNKLER_BLICK = 50
PREDIGER_BONUS_VS_VERDERBT = 1.2

FAECHER_MALUS = 10            # v3: vorher 20
FAECHER_SCHWELLE = 0.5        # v3: Fächerschuss, sobald Gegner ≤ 50 % Leben (oder letzter Schuss)
TINKTUR_HEILUNG = 20
TINKTUR_SCHWELLE = 0.5
STAUBWOLKE_MALUS = 25
KOPFGELD_TREFFER_BONUS = 10   # v4: Kopfgeldjäger gegen Spieler mit offenem Kopfgeld

# ---------------------------------------------------------------------------
# KÄMPFER
# ---------------------------------------------------------------------------

STANDARD_ZIEL = {"Kopf": 1 / 3, "Körper": 1 / 3, "Beine": 1 / 3}   # v2: vorher 30/50/20
STANDARD_BEWEGUNG = {"Ducken": 1 / 3, "Seitsprung": 1 / 3, "Springen": 1 / 3}


@dataclass
class Kaempfer:
    name: str
    klasse: str = "Revolverheld"
    zielen: int = 10
    reflexe: int = 10
    zaehigkeit: int = 10
    nerven: int = 10
    instinkt: int = 10
    waffenfaktor: float = 1.0
    schwarzerz: bool = False
    verderbnis: int = 0
    kopfgeld: int = 0             # v4: offenes Kopfgeld in Dollar
    ziel_gewichte: dict = field(default_factory=lambda: dict(STANDARD_ZIEL))
    bewegung_gewichte: dict = field(default_factory=lambda: dict(STANDARD_BEWEGUNG))

    @property
    def max_leben(self) -> int:
        return LEBEN_BASIS + LEBEN_PRO_ZAEHIGKEIT * self.zaehigkeit


@dataclass
class Zustand:
    k: Kaempfer
    leben: float
    schuesse: int = 0
    bein_debuff: bool = False
    staubwolke_auf_mir: bool = False
    segen_aktiv: bool = False
    faehigkeit_frei: bool = True
    instinkt_frei: bool = False
    dunkler_blick_frei: bool = False
    schaden_verursacht: float = 0.0
    treffer: int = 0


# ---------------------------------------------------------------------------
# BUILDS
# ---------------------------------------------------------------------------

BUILDS = {
    "jack": Kaempfer("Jack", "Revolverheld", zielen=12, reflexe=8, zaehigkeit=9, nerven=10, instinkt=8),
    "rosa": Kaempfer("Rosa", "Kopfgeldjäger", zielen=9, reflexe=10, zaehigkeit=10, nerven=11, instinkt=10),
    "vater": Kaempfer("Vater Abel", "Prediger", zielen=9, reflexe=9, zaehigkeit=11, nerven=14, instinkt=7),
    "doc": Kaempfer("Doc Mercy", "Quacksalber", zielen=9, reflexe=10, zaehigkeit=9, nerven=10, instinkt=12),
    "silas": Kaempfer("Silas", "Prospektor", zielen=10, reflexe=11, zaehigkeit=11, nerven=9, instinkt=9),
    "ash": Kaempfer("Ash", "Revolverheld", zielen=11, reflexe=10, zaehigkeit=9, nerven=8, instinkt=10,
                    schwarzerz=True, verderbnis=60),
}

KLASSEN = ["Revolverheld", "Kopfgeldjäger", "Prediger", "Quacksalber", "Prospektor"]


# ---------------------------------------------------------------------------
# MECHANIK
# ---------------------------------------------------------------------------

def gewichtet(rng: random.Random, gewichte: dict) -> str:
    return rng.choices(list(gewichte), weights=list(gewichte.values()))[0]


def trefferchance(schuetze: Kaempfer, ziel_k: Kaempfer, zone: str, gekontert: bool,
                  bein_debuff: bool, staubwolke: bool, extra: int = 0) -> int:
    _, mod, _ = ZONEN[zone]
    if zone == "Kopf":
        mod += max(0, schuetze.nerven - 10) * NERVEN_KOPF_PRO_PUNKT
    p = TREFFER_BASIS + TREFFER_PRO_PUNKT * (schuetze.zielen - ziel_k.reflexe) + mod
    if gekontert:
        p -= KONTER_MALUS
    if bein_debuff:
        p += BEIN_DEBUFF
    if staubwolke:
        p -= STAUBWOLKE_MALUS
    p += extra
    return max(TREFFER_MIN, min(TREFFER_MAX, p))


def beste_zone_gegen(schuetze: Kaempfer, gegner: Kaempfer) -> str:
    """Zielwahl mit maximalem Erwartungsschaden gegen die Bewegungsgewichte des Gegners."""
    best, best_ev = "Körper", -1.0
    for zone, (dmg, _, konter) in ZONEN.items():
        p_konter = gegner.bewegung_gewichte.get(konter, 0)
        p_hit = (
            p_konter * trefferchance(schuetze, gegner, zone, True, False, False)
            + (1 - p_konter) * trefferchance(schuetze, gegner, zone, False, False, False)
        ) / 100
        ev = p_hit * dmg
        if zone == "Beine":   # v3: Folgewert des Debuffs auf den nächsten Schuss einrechnen
            ev += p_hit * BEIN_DEBUFF / 100 * ZONEN["Körper"][0]
        if ev > best_ev:
            best, best_ev = zone, ev
    return best


class Duell:
    def __init__(self, a: Kaempfer, b: Kaempfer, rng: random.Random, log: bool = False):
        self.rng = rng
        self.log_an = log
        self.zeilen: list[str] = []
        self.a = self._init(a)
        self.b = self._init(b)

    def _init(self, k: Kaempfer) -> Zustand:
        z = Zustand(k, float(k.max_leben))
        z.segen_aktiv = k.klasse == "Prediger"
        z.dunkler_blick_frei = k.verderbnis >= VERDERBNIS_DUNKLER_BLICK
        return z

    def log(self, text: str) -> None:
        if self.log_an:
            self.zeilen.append(text)

    def standoff(self) -> tuple[Zustand, Zustand]:
        def wurf(z: Zustand) -> tuple:
            return (z.k.reflexe + NERVEN_STANDOFF_FAKTOR * z.k.nerven + self.rng.randint(1, 20), z.k.reflexe, self.rng.random())
        wa, wb = wurf(self.a), wurf(self.b)
        self.log(f"Standoff: {self.a.k.name} {wa[0]} – {self.b.k.name} {wb[0]}")
        return (self.a, self.b) if wa > wb else (self.b, self.a)

    def nerven_wackeln(self, z: Zustand) -> bool:
        if z.leben / z.k.max_leben >= NERVEN_SCHWELLE:
            return False
        chance = max(0, NERVEN_BASIS - NERVEN_PRO_PUNKT * z.k.nerven)
        return self.rng.random() * 100 < chance

    def zug(self, s: Zustand, g: Zustand) -> None:
        s.schuesse += 1
        k, gk = s.k, g.k

        # Quacksalber: Tinktur statt Schuss
        if (k.klasse == "Quacksalber" and s.faehigkeit_frei
                and s.leben / k.max_leben < TINKTUR_SCHWELLE):
            s.faehigkeit_frei = False
            s.leben = min(k.max_leben, s.leben + TINKTUR_HEILUNG)
            self.log(f"{k.name} kippt eine Tinktur: +{TINKTUR_HEILUNG} Leben ({s.leben:.0f}).")
            return

        # Prospektor: Staubwolke als freie Aktion im ersten Zug
        # (Flag sitzt beim Gegner: sein nächster Schuss ist geschwächt)
        if k.klasse == "Prospektor" and s.faehigkeit_frei:
            s.faehigkeit_frei = False
            g.staubwolke_auf_mir = True
            self.log(f"{k.name} tritt eine Staubwolke los.")

        # Zielwahl
        wackelt = self.nerven_wackeln(s)
        if wackelt:
            zone = self.rng.choice(list(ZONEN))
            self.log(f"{k.name} zittert – der Schuss geht irgendwohin.")
        elif k.klasse == "Kopfgeldjäger":
            zone = beste_zone_gegen(k, gk)
        else:
            zone = gewichtet(self.rng, k.ziel_gewichte)

        bewegung = (self.rng.choice(BEWEGUNGEN) if self.nerven_wackeln(g)
                    else gewichtet(self.rng, gk.bewegung_gewichte))
        gekontert = ZONEN[zone][2] == bewegung

        # Dunkler Blick (einmal sicher) / Instinkt (jeder Schuss, kleine Chance)
        if gekontert and not wackelt:
            if s.dunkler_blick_frei:
                s.dunkler_blick_frei = False
                quelle = "Dunkler Blick"
            elif self.rng.random() * 100 < k.instinkt * INSTINKT_PRO_PUNKT:
                quelle = "Instinkt"
            else:
                quelle = None
            if quelle:
                zone = max((z for z in ZONEN if ZONEN[z][2] != bewegung),
                           key=lambda z: ZONEN[z][0] * trefferchance(k, gk, z, False, False, False))
                gekontert = False
                self.log(f"{k.name} liest die Bewegung ({quelle}) und zielt um.")

        # Revolverheld: Fächerschuss, sobald der Gegner angeschlagen ist oder beim letzten Schuss
        schuesse = 1
        extra = 0
        if (k.klasse == "Revolverheld" and s.faehigkeit_frei
                and (g.leben / gk.max_leben <= FAECHER_SCHWELLE
                     or s.schuesse == SCHUESSE_PRO_SEITE)):
            s.faehigkeit_frei = False
            schuesse, extra = 2, -FAECHER_MALUS
            self.log(f"{k.name} fächert den Hahn!")

        staub = s.staubwolke_auf_mir
        s.staubwolke_auf_mir = False
        if k.klasse == "Kopfgeldjäger" and gk.kopfgeld > 0:
            extra += KOPFGELD_TREFFER_BONUS

        for _ in range(schuesse):
            if g.leben <= 0:
                break
            p = trefferchance(k, gk, zone, gekontert, g.bein_debuff, staub, extra)
            g.bein_debuff = False
            if self.rng.random() * 100 < p:
                dmg = ZONEN[zone][0] * k.waffenfaktor
                if k.schwarzerz:
                    dmg *= SCHWARZERZ_SCHADEN
                if k.klasse == "Prediger" and gk.verderbnis >= VERDERBNIS_DUNKLER_BLICK:
                    dmg *= PREDIGER_BONUS_VS_VERDERBT
                if g.segen_aktiv:
                    g.segen_aktiv = False
                    dmg *= SEGEN_FAKTOR
                    self.log(f"Der Segen schützt {gk.name}.")
                g.leben -= dmg
                s.schaden_verursacht += dmg
                s.treffer += 1
                if zone == "Beine":
                    g.bein_debuff = True
                self.log(f"{k.name} → {zone}, {gk.name} {bewegung.lower()}: {p} % – "
                         f"TREFFER, {dmg:.0f} Schaden ({max(0, g.leben):.0f} übrig)")
            else:
                self.log(f"{k.name} → {zone}, {gk.name} {bewegung.lower()}: {p} % – daneben")

    def kampf(self) -> Optional[str]:
        erster, zweiter = self.standoff()
        self.log(f"{erster.k.name} zieht zuerst.")
        for _ in range(SCHUESSE_PRO_SEITE):
            for s, g in ((erster, zweiter), (zweiter, erster)):
                self.zug(s, g)
                if g.leben <= 0:
                    self.log(f"{g.k.name} geht zu Boden. {s.k.name} gewinnt.")
                    self.ko = True
                    return s.k.name
        self.ko = False
        qa = self.a.leben / self.a.k.max_leben
        qb = self.b.leben / self.b.k.max_leben
        if abs(qa - qb) < 1e-9:
            self.log("Trommeln leer – unentschieden.")
            return None
        sieger = self.a if qa > qb else self.b
        self.log(f"Trommeln leer. {sieger.k.name} steht besser da und gewinnt.")
        return sieger.k.name


# ---------------------------------------------------------------------------
# AUSWERTUNG
# ---------------------------------------------------------------------------

def match(a: Kaempfer, b: Kaempfer, n: int, rng: random.Random) -> dict:
    siege = {a.name: 0, b.name: 0, None: 0}
    ko = 0
    for _ in range(n):
        d = Duell(a, b, rng)
        siege[d.kampf()] += 1
        ko += d.ko
    return {"a": siege[a.name] / n, "b": siege[b.name] / n,
            "remis": siege[None] / n, "ko": ko / n}


def cmd_demo(args, rng):
    d = Duell(BUILDS["jack"], BUILDS["rosa"], rng, log=True)
    d.kampf()
    print("\n".join(d.zeilen))


def cmd_match(args, rng):
    a, b = BUILDS[args.a], BUILDS[args.b]
    r = match(a, b, args.n, rng)
    print(f"{a.name} ({a.klasse}) vs {b.name} ({b.klasse}), {args.n} Duelle")
    print(f"  {a.name}: {r['a']:.1%}   {b.name}: {r['b']:.1%}   "
          f"Remis: {r['remis']:.1%}   K.O.-Quote: {r['ko']:.1%}")


def cmd_klassen(args, rng):
    print(f"Klassen-Matrix: Siegquote Zeile gegen Spalte, alle Werte 10, {args.n} Duelle je Paar\n")
    kurz = [k[:6] for k in KLASSEN]
    print(f"{'':14}" + "".join(f"{k:>9}" for k in kurz) + f"{'Schnitt':>10}")
    for ka in KLASSEN:
        zeile, summe = [], 0.0
        for kb in KLASSEN:
            if ka == kb:
                zeile.append("    –    ")
                continue
            r = match(Kaempfer("A", ka), Kaempfer("B", kb), args.n, rng)
            summe += r["a"]
            zeile.append(f"{r['a']:>8.1%} ")
        print(f"{ka:14}" + "".join(zeile) + f"{summe / (len(KLASSEN) - 1):>9.1%}")


def cmd_sweep(args, rng):
    print(f"Wertvorsprung: A hat +x in einem Wert, sonst alle 10 (Revolverheld vs Revolverheld)\n")
    werte = ["zielen", "reflexe", "zaehigkeit", "nerven", "instinkt"]
    print(f"{'Vorsprung':>10}" + "".join(f"{w:>12}" for w in werte))
    for x in (0, 2, 4, 6, 10):
        zeile = []
        for w in werte:
            a = Kaempfer("A")
            setattr(a, w, 10 + x)
            r = match(a, Kaempfer("B"), args.n, rng)
            zeile.append(f"{r['a']:>11.1%} ")
        print(f"{'+' + str(x):>10}" + "".join(zeile))


def cmd_zielwahl(args, rng):
    print("Reine Zielstrategien gegen Standard-Verteidiger (gleichmäßige Bewegung)\n")
    for zone in ZONEN:
        a = Kaempfer("A", "Prediger", ziel_gewichte={z: (1.0 if z == zone else 0.0) for z in ZONEN})
        r = match(a, Kaempfer("B", "Prediger"), args.n, rng)
        print(f"  immer {zone:7}: {r['a']:.1%} Siege")
    print("\nReine Bewegung gegen Standard-Schützen\n")
    for bew in BEWEGUNGEN:
        a = Kaempfer("A", "Prediger", bewegung_gewichte={x: (1.0 if x == bew else 0.0) for x in BEWEGUNGEN})
        r = match(a, Kaempfer("B", "Prediger"), args.n, rng)
        print(f"  immer {bew:10}: {r['a']:.1%} Siege")


def cmd_kopfgeld(args, rng):
    print("Kopfgeldjäger gegen jede Klasse: Ziel ohne / mit offenem Kopfgeld\n")
    for kb in KLASSEN:
        if kb == "Kopfgeldjäger":
            continue
        ohne = match(Kaempfer("A", "Kopfgeldjäger"), Kaempfer("B", kb), args.n, rng)
        mit = match(Kaempfer("A", "Kopfgeldjäger"), Kaempfer("B", kb, kopfgeld=100), args.n, rng)
        print(f"  vs {kb:13}: {ohne['a']:.1%} → {mit['a']:.1%}")


def main():
    p = argparse.ArgumentParser(description="Ore & Omen Duell-Simulator")
    p.add_argument("-n", type=int, default=10000, help="Duelle pro Paarung")
    p.add_argument("--seed", type=int, default=None)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo")
    m = sub.add_parser("match")
    m.add_argument("a", choices=BUILDS)
    m.add_argument("b", choices=BUILDS)
    sub.add_parser("klassen")
    sub.add_parser("sweep")
    sub.add_parser("zielwahl")
    sub.add_parser("kopfgeld")
    sub.add_parser("alles")
    args = p.parse_args()
    rng = random.Random(args.seed)

    if args.cmd == "alles":
        for f in (cmd_klassen, cmd_sweep, cmd_zielwahl, cmd_kopfgeld):
            f(args, rng)
            print("\n" + "-" * 70 + "\n")
    else:
        {"demo": cmd_demo, "match": cmd_match, "klassen": cmd_klassen,
         "sweep": cmd_sweep, "zielwahl": cmd_zielwahl, "kopfgeld": cmd_kopfgeld}[args.cmd](args, rng)


if __name__ == "__main__":
    main()

"""Sanity checks that constants match the binding values in docs/."""

from app.game import constants as c


def _tier(value, tiers):
    code = tiers[0][1]
    for bound, name in tiers:
        if value >= bound:
            code = name
    return code


def test_reputation_tiers_match_doc():
    # 02-fraktionen.md
    cases = {
        -1000: "hated",
        -600: "hated",
        -599: "hostile",
        -200: "hostile",
        -199: "neutral",
        199: "neutral",
        200: "known",
        499: "known",
        500: "respected",
        799: "respected",
        800: "trusted",
        999: "trusted",
        1000: "honored",
    }
    for value, code in cases.items():
        assert _tier(value, c.REPUTATION_TIERS) == code, value


def test_side_effect_example():
    # +40 Aschenbande → −20 Kompanie, −20 Orden, −4 Hüter
    m = c.REPUTATION_SIDE_EFFECTS["ash_gang"]
    assert [40 * m[f] for f in ("company", "order", "keepers")] == [20, 20, 4]


def test_corruption_tiers_match_doc():
    cases = {
        0: "pure",
        24: "pure",
        25: "marked",
        49: "marked",
        50: "tainted",
        74: "tainted",
        75: "possessed",
        99: "possessed",
        100: "lost",
    }
    for value, code in cases.items():
        assert _tier(value, c.CORRUPTION_TIERS) == code, value


def test_wanted_tiers():
    assert _tier(1, c.WANTED_TIERS) == "wanted"
    assert _tier(999, c.WANTED_TIERS) == "wanted"
    assert _tier(1000, c.WANTED_TIERS) == "dangerous"
    assert _tier(5000, c.WANTED_TIERS) == "notorious"


def test_chapel_level_10_matches_balancing_goal():
    # 06-verderbnis.md: Kapelle Stufe 10 nimmt −6 pro Tag
    assert c.CHAPEL_BASE + 10 * c.CHAPEL_PER_LEVEL == 6


def test_duel_constants_match_simulator():
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parents[2] / "tools" / "duel_sim.py"
    spec = importlib.util.spec_from_file_location("duel_sim", path)
    sim = importlib.util.module_from_spec(spec)
    sys.modules["duel_sim"] = sim  # dataclasses need the module registered
    spec.loader.exec_module(sim)

    pairs = {
        "LIFE_BASE": "LEBEN_BASIS",
        "LIFE_PER_TOUGHNESS": "LEBEN_PRO_ZAEHIGKEIT",
        "SHOTS_PER_SIDE": "SCHUESSE_PRO_SEITE",
        "HIT_BASE": "TREFFER_BASIS",
        "HIT_PER_POINT": "TREFFER_PRO_PUNKT",
        "COUNTER_PENALTY": "KONTER_MALUS",
        "HIT_MIN": "TREFFER_MIN",
        "HIT_MAX": "TREFFER_MAX",
        "LEG_DEBUFF": "BEIN_DEBUFF",
        "NERVE_THRESHOLD": "NERVEN_SCHWELLE",
        "NERVE_BASE": "NERVEN_BASIS",
        "NERVE_PER_POINT": "NERVEN_PRO_PUNKT",
        "NERVE_STANDOFF_FACTOR": "NERVEN_STANDOFF_FAKTOR",
        "NERVE_HEADSHOT_PER_POINT": "NERVEN_KOPF_PRO_PUNKT",
        "INSTINCT_PER_POINT": "INSTINKT_PRO_PUNKT",
        "BLACK_ORE_BULLET_DAMAGE": "SCHWARZERZ_SCHADEN",
        "BLESSING_FACTOR": "SEGEN_FAKTOR",
        "DARK_SIGHT_CORRUPTION": "VERDERBNIS_DUNKLER_BLICK",
        "PREACHER_BONUS_VS_CORRUPTED": "PREDIGER_BONUS_VS_VERDERBT",
        "SHADOW_STEP_CORRUPTION": "VERDERBNIS_SCHATTENSCHRITT",
        "SHADOW_STEP_PENALTY": "SCHATTENSCHRITT_MALUS",
        "FAN_SHOT_PENALTY": "FAECHER_MALUS",
        "FAN_SHOT_THRESHOLD": "FAECHER_SCHWELLE",
        "TINCTURE_HEAL": "TINKTUR_HEILUNG",
        "TINCTURE_THRESHOLD": "TINKTUR_SCHWELLE",
        "DUST_CLOUD_PENALTY": "STAUBWOLKE_MALUS",
        "BOUNTY_HUNTER_HIT_BONUS": "KOPFGELD_TREFFER_BONUS",
    }
    for ours, theirs in pairs.items():
        assert getattr(c, ours) == getattr(sim, theirs), ours
    zones = {"head": "Kopf", "body": "Körper", "legs": "Beine"}
    for zone, de in zones.items():
        assert c.ZONES[zone][:2] == sim.ZONEN[de][:2]

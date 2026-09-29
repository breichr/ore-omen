import pytest

from app.content import buildings, parse_buildings

DOC_BUILDINGS = {
    "main_house",
    "storehouse",
    "lumber_yard",
    "cattle_pen",
    "distillery",
    "smithy",
    "dig_site",
    "shooting_range",
    "apothecary",
    "chapel",
    "map_room",
    "palisade",
    "watchtower",
    "kennel",
    "salt_circle",
    "ore_shrine",
    "boneyard",
    "whisper_well",
}


def test_all_buildings_from_doc_are_defined():
    assert set(buildings()) == DOC_BUILDINGS


def test_base_values_match_doc():
    b = buildings()
    assert b["main_house"].cost == {"wood": 100, "iron": 50, "dollars": 100}
    assert b["main_house"].time_min == 20
    assert b["storehouse"].cost == {"wood": 80, "iron": 20}
    assert b["lumber_yard"].produces == {"wood": 20}
    assert b["dig_site"].produces == {"iron": 10, "silver": 2, "black_ore": 0.5}
    assert b["dig_site"].produces_from_level == {"black_ore": 5}
    for code in ("shooting_range", "apothecary", "chapel", "map_room"):
        assert b[code].cost == {"wood": 120, "iron": 60, "dollars": 150}
        assert b[code].time_min == 15
    for code in ("palisade", "watchtower", "kennel", "salt_circle"):
        assert b[code].cost == {"wood": 100, "iron": 80} and b[code].time_min == 12
    for code in ("ore_shrine", "boneyard", "whisper_well"):
        assert b[code].black_ore_per_level == 5


def test_chapel_and_ore_shrine_exclude_each_other():
    b = buildings()
    assert b["chapel"].excludes == ("ore_shrine",)
    assert b["ore_shrine"].excludes == ("chapel",)


def _minimal(**extra):
    base = {
        "main_house": {"category": "core", "name": "H", "cost": {"wood": 1}, "time_min": 1},
        "storehouse": {"category": "core", "name": "L", "cost": {"wood": 1}, "time_min": 1},
    }
    base.update(extra)
    return {"buildings": base}


@pytest.mark.parametrize(
    "bad",
    [
        {"x": {"category": "nope", "name": "X", "cost": {"wood": 1}, "time_min": 1}},
        {"x": {"category": "core", "name": "X", "cost": {"gold": 1}, "time_min": 1}},
        {
            "x": {
                "category": "core",
                "name": "X",
                "cost": {"wood": 1},
                "time_min": 1,
                "excludes": ["main_house"],
            }
        },
    ],
)
def test_parser_rejects_invalid_content(bad):
    with pytest.raises(ValueError):
        parse_buildings(_minimal(**bad))

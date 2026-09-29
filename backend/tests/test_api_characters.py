import pytest

from tests.conftest import register

ROSA = {"name": "Rosa", "class": "bounty_hunter", "allocation": {"dexterity": 2, "intellect": 2}}


def test_requires_login(client):
    assert client.post("/characters", json=ROSA).status_code == 401


def test_create_character(client):
    register(client)
    r = client.post("/characters", json=ROSA)
    assert r.status_code == 201, r.text
    ch = r.json()
    assert ch["name"] == "Rosa"
    assert ch["character_class"] == "bounty_hunter"
    assert ch["level"] == 1
    assert ch["attributes"] == {"strength": 5, "dexterity": 7, "intellect": 7, "charisma": 5}
    assert ch["unspent_attribute_points"] == 0
    assert ch["unspent_skill_points"] == 5
    assert ch["dollars"] == 150
    assert ch["corruption"] == 0
    assert ch["region"] == "hollow_creek"
    # Duellwert = 0 Skill + floor(Attribut / 2); Leben = 40 + 4 × Zähigkeit
    assert ch["duel_values"] == {
        "aim": 3,
        "reflexes": 3,
        "toughness": 2,
        "nerve": 2,
        "instinct": 3,
    }
    assert ch["max_life"] == 48
    assert client.get("/me").json()["character"]["name"] == "Rosa"


def test_one_character_per_account(client):
    register(client)
    client.post("/characters", json=ROSA)
    r = client.post("/characters", json={**ROSA, "name": "Rosalie"})
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "character_exists"


def test_name_unique_case_insensitive(client):
    register(client)
    client.post("/characters", json=ROSA)
    client.cookies.clear()
    register(client, username="jack")
    r = client.post("/characters", json={**ROSA, "name": "  rOSA "})
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "name_taken"


@pytest.mark.parametrize(
    ("patch", "code"),
    [
        ({"name": "Al"}, "name_length"),
        ({"name": "Jack99"}, "name_chars"),
        ({"class": "wizard"}, "unknown_class"),
        ({"allocation": {"strength": 3}}, "points_not_spent"),
        ({"allocation": {"strength": 5, "charisma": -1}}, "negative_points"),
        ({"allocation": {"luck": 4}}, "unknown_attribute"),
    ],
)
def test_rule_errors(client, patch, code):
    register(client)
    r = client.post("/characters", json={**ROSA, **patch})
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == code

import pytest

from app.game import constants as c
from app.game.character import (
    RuleError,
    create_character,
    duel_value,
    duel_values,
    max_life,
    name_key,
    skill_cap,
    starting_attributes,
    validate_name,
)


class TestName:
    @pytest.mark.parametrize(
        "name", ["Rosa", "Vater Abel", "Mae Holloway", "O'Brien", "Jean-Luc", "Jörg Übel", "Ada"]
    )
    def test_valid(self, name):
        assert validate_name(name) == name

    def test_normalizes_whitespace(self):
        assert validate_name("  Doc   Mercy ") == "Doc Mercy"

    @pytest.mark.parametrize("name", ["Al", "A" * 21, "   ", ""])
    def test_length(self, name):
        with pytest.raises(RuleError) as e:
            validate_name(name)
        assert e.value.code == "name_length"

    @pytest.mark.parametrize("name", ["Jack1", "Jack_", "Jack!", "-Jack", "Jack--Hi", "<b>x</b>"])
    def test_chars(self, name):
        with pytest.raises(RuleError) as e:
            validate_name(name)
        assert e.value.code == "name_chars"

    def test_boundaries(self):
        assert validate_name("Ash") == "Ash"
        assert validate_name("A" * 20) == "A" * 20

    def test_key_is_case_insensitive(self):
        assert name_key("Silas Crane") == name_key("silas  CRANE")


class TestAttributes:
    def test_start_values_5_plus_4_free(self):
        attrs = starting_attributes({"dexterity": 3, "charisma": 1})
        assert attrs == {"strength": 5, "dexterity": 8, "intellect": 5, "charisma": 6}
        assert sum(attrs.values()) == 4 * 5 + 4

    @pytest.mark.parametrize("alloc", [{}, {"strength": 3}, {"strength": 5}])
    def test_all_four_points_must_be_spent(self, alloc):
        with pytest.raises(RuleError) as e:
            starting_attributes(alloc)
        assert e.value.code == "points_not_spent"

    def test_negative(self):
        with pytest.raises(RuleError):
            starting_attributes({"strength": 5, "charisma": -1})

    def test_unknown(self):
        with pytest.raises(RuleError):
            starting_attributes({"luck": 4})


class TestSkills:
    def test_twelve_skills_three_per_attribute(self):
        assert len(c.SKILLS) == 12
        assert all(len(s) == 3 for s in c.SKILLS_BY_ATTRIBUTE.values())
        assert set(c.DUEL_SKILLS) <= set(c.SKILLS)

    def test_cap_is_level_plus_two(self):
        assert skill_cap(1) == 3
        assert skill_cap(10) == 12


class TestDuelValues:
    def test_formula(self):
        # Duellwert = Skillpunkte + floor(Attribut / 2) + Ausrüstung
        assert duel_value(3, 9, 1) == 3 + 4 + 1
        assert duel_value(0, 5) == 2

    def test_mapping_uses_base_attribute(self):
        attrs = {"strength": 6, "dexterity": 9, "intellect": 5, "charisma": 7}
        v = duel_values(attrs, {"aim": 2}, {"aim": 1})
        assert v == {"aim": 2 + 4 + 1, "reflexes": 4, "toughness": 3, "nerve": 3, "instinct": 2}

    def test_life(self):
        # 04-duelle.md: Leben = 40 + 4 × Zähigkeit (80 bei Zähigkeit 10)
        assert max_life(10) == 80


def test_create_character():
    ch = create_character(" Rosa ", "bounty_hunter", {"dexterity": 2, "intellect": 2})
    assert ch.name == "Rosa"
    assert ch.level == 1
    assert ch.unspent_skill_points == 5
    assert ch.unspent_attribute_points == 0
    assert ch.dollars == 150
    assert ch.region == "hollow_creek"


def test_unknown_class():
    with pytest.raises(RuleError) as e:
        create_character("Rosa", "wizard", {"dexterity": 4})
    assert e.value.code == "unknown_class"

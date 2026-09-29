from datetime import UTC, date, datetime

import pytest

from app.game.character import RuleError
from app.game.gameday import game_day, next_reset
from app.game.reputation import apply, swear
from app.game.travel import base_minutes, travel_seconds

ZERO = {"company": 0, "order": 0, "ash_gang": 0, "keepers": 0}


class TestApply:
    def test_matrix_example(self):
        r = apply(ZERO, {"ash_gang": 40}, 0, None)
        assert r.values == {"company": -20, "order": -20, "ash_gang": 40, "keepers": -4}

    def test_capped_gain_has_no_side_effects(self):
        start = {**ZERO, "company": 790}
        r = apply(start, {"company": 40}, 0, None)
        assert r.values["company"] == 799  # no oath
        assert r.values["order"] == -2  # 9 × 25 % = 2,25 → 2
        r = apply({**ZERO, "company": 799}, {"company": 40}, 0, None)
        assert r.deltas == {}

    def test_losses_have_no_side_effects_and_floor(self):
        r = apply({**ZERO, "order": -990}, {"order": -40}, 0, None)
        assert r.values["order"] == -1000
        assert r.deltas == {"order": -10}

    def test_cap_cuts_existing_value(self):
        r = apply({**ZERO, "order": 600}, {}, 50, None)  # corruption ≥ 50
        assert r.values["order"] == 199

    def test_oath_raises_cap(self):
        r = apply({**ZERO, "company": 799}, {"company": 30}, 0, "company")
        assert r.values["company"] == 829

    def test_unknown_faction(self):
        with pytest.raises(RuleError):
            apply(ZERO, {"sheriff": 10}, 0, None)


class TestOath:
    def test_needs_respected(self):
        with pytest.raises(RuleError) as e:
            swear({**ZERO, "company": 499}, None, "company")
        assert e.value.code == "reputation_too_low"
        assert swear({**ZERO, "company": 500}, None, "company").oath == "company"

    def test_switch_costs_half(self):
        r = swear({**ZERO, "company": 799, "ash_gang": 600}, "company", "ash_gang")
        assert (r.oath, r.lost, r.values["company"]) == ("ash_gang", 400, 399)  # 399,5 → 400

    @pytest.mark.parametrize(
        ("faction", "oath", "code"),
        [("order", None, "no_oath_faction"), ("company", "company", "already_sworn")],
    )
    def test_errors(self, faction, oath, code):
        with pytest.raises(RuleError) as e:
            swear({**ZERO, "company": 900, "order": 900}, oath, faction)
        assert e.value.code == code


class TestTravel:
    def test_table(self):
        assert base_minutes("hollow_creek", "pine_slope") == 15
        assert base_minutes("salt_flats", "hollow_creek") == 45
        assert base_minutes("pine_slope", "deep_vein") == 45  # via town
        assert base_minutes("salt_flats", "silent_mission") == 60  # 75 capped

    def test_reductions(self):
        assert travel_seconds("hollow_creek", "pine_slope") == 900
        assert travel_seconds("hollow_creek", "pine_slope", map_room_level=5) == 810
        assert travel_seconds("hollow_creek", "pine_slope", keepers_reputation=800) == 765

    def test_gorge_needs_keepers_known(self):
        with pytest.raises(RuleError) as e:
            travel_seconds("hollow_creek", "the_gorge", keepers_reputation=199)
        assert e.value.code == "gorge_closed"
        assert travel_seconds("hollow_creek", "the_gorge", keepers_reputation=200) == 3600

    def test_same_or_unknown_region(self):
        for a, b in [("pine_slope", "pine_slope"), ("pine_slope", "mars")]:
            with pytest.raises(RuleError):
                base_minutes(a, b)


class TestGameDay:
    def test_changes_at_4_vienna(self):
        # Winter: Vienna = UTC+1 → 04:00 local = 03:00 UTC
        assert game_day(datetime(2026, 1, 10, 2, 59, tzinfo=UTC)) == date(2026, 1, 9)
        assert game_day(datetime(2026, 1, 10, 3, 0, tzinfo=UTC)) == date(2026, 1, 10)
        # Summer: UTC+2 → 02:00 UTC
        assert game_day(datetime(2026, 7, 10, 1, 59, tzinfo=UTC)) == date(2026, 7, 9)
        assert game_day(datetime(2026, 7, 10, 2, 0, tzinfo=UTC)) == date(2026, 7, 10)

    def test_next_reset(self):
        assert next_reset(datetime(2026, 1, 10, 12, 0, tzinfo=UTC)) == datetime(
            2026, 1, 11, 3, 0, tzinfo=UTC
        )
        # DST switch night (29 Mar 2026): reset at 04:00 CEST = 02:00 UTC
        assert next_reset(datetime(2026, 3, 28, 12, 0, tzinfo=UTC)) == datetime(
            2026, 3, 29, 2, 0, tzinfo=UTC
        )

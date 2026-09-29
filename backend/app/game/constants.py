"""Central balancing constants for Ore & Omen.

Every number here comes from docs/. The docs are binding: change a value in the
matching doc first, then here. Content (building base values, quests, items)
lives in content/, not here.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Time (docs/08-technik.md)
# ---------------------------------------------------------------------------

SERVER_TIMEZONE: Final = "Europe/Vienna"
DAILY_RESET_HOUR: Final = 4  # 04:00 server time
WEEKLY_RESET_WEEKDAY: Final = 0  # Monday (datetime.weekday())
WEEKLY_RESET_HOUR: Final = 0  # Monday 00:00 server time
DEFAULT_USER_TIMEZONE: Final = SERVER_TIMEZONE

# ---------------------------------------------------------------------------
# Character (docs/01-welt.md)
# ---------------------------------------------------------------------------

ATTRIBUTES: Final = ("strength", "dexterity", "intellect", "charisma")
ATTRIBUTE_START_VALUE: Final = 5
ATTRIBUTE_START_FREE_POINTS: Final = 4
ATTRIBUTE_POINTS_PER_LEVEL: Final = 2

# Three skills per attribute. The five duel values are skills.
SKILLS_BY_ATTRIBUTE: Final[dict[str, tuple[str, str, str]]] = {
    "strength": ("toughness", "building", "carrying"),
    "dexterity": ("aim", "reflexes", "sleight_of_hand"),
    "intellect": ("instinct", "crafting", "cartography"),
    "charisma": ("nerve", "trade", "persuasion"),
}
SKILLS: Final = tuple(s for skills in SKILLS_BY_ATTRIBUTE.values() for s in skills)
DUEL_SKILLS: Final = ("aim", "reflexes", "toughness", "nerve", "instinct")
SKILL_START_POINTS: Final = 5
SKILL_POINTS_PER_LEVEL: Final = 3
SKILL_CAP_OVER_LEVEL: Final = 2  # a skill may have at most level + 2 points

CLASSES: Final = ("gunslinger", "prospector", "quack", "preacher", "bounty_hunter")
SECOND_CLASS_MIN_LEVEL: Final = 25  # phase 3

CHARACTER_NAME_MIN_LEN: Final = 3
CHARACTER_NAME_MAX_LEN: Final = 20

START_LEVEL: Final = 1

# Experience (docs/01-welt.md, "Erfahrung und Stufen")
XP_BASE: Final = 100  # XP for level n → n+1 = 100 × n^1.5
XP_EXPONENT: Final = 1.5
START_REGION: Final = "hollow_creek"

REGIONS: Final = (
    "hollow_creek",
    "pine_slope",  # Kiefernhang
    "deep_vein",  # Die Tiefe Ader
    "salt_flats",  # Salzebene
    "silent_mission",  # Stille Mission
    "the_gorge",  # Die Schlucht
)
TRAVEL_MINUTES_MIN: Final = 15
TRAVEL_MINUTES_MAX: Final = 60
# Minutes from Hollow Creek (docs/01-welt.md); outer ↔ outer = sum, capped at max
TRAVEL_MINUTES_FROM_TOWN: Final[dict[str, int]] = {
    "pine_slope": 15,
    "deep_vein": 30,
    "silent_mission": 30,
    "salt_flats": 45,
    "the_gorge": 60,
}
GORGE_MIN_KEEPERS_REPUTATION: Final = 200  # "known"

RESOURCES: Final = ("wood", "iron", "cattle", "whiskey", "silver", "salt", "black_ore")

# ---------------------------------------------------------------------------
# Factions & reputation (docs/02-fraktionen.md)
# ---------------------------------------------------------------------------

FACTIONS: Final = ("company", "order", "ash_gang", "keepers")
REPUTATION_MIN: Final = -1000
REPUTATION_MAX: Final = 1000
REPUTATION_START: Final = 0

# (lower bound inclusive, code); a value belongs to the last tier whose bound it reaches
REPUTATION_TIERS: Final = (
    (-1000, "hated"),
    (-599, "hostile"),
    (-199, "neutral"),
    (200, "known"),
    (500, "respected"),
    (800, "trusted"),
    (1000, "honored"),
)

# Loss at column faction as a fraction of a direct gain at row faction.
REPUTATION_SIDE_EFFECTS: Final[dict[str, dict[str, float]]] = {
    "company": {"order": 0.25, "ash_gang": 0.50, "keepers": 0.25},
    "order": {"company": 0.25, "ash_gang": 0.50, "keepers": 0.0},
    "ash_gang": {"company": 0.50, "order": 0.50, "keepers": 0.10},
    "keepers": {"company": 0.25, "order": 0.0, "ash_gang": 0.10},
}

REPUTATION_DAILY_JOB_MIN: Final = 10
REPUTATION_DAILY_JOB_MAX: Final = 20
REPUTATION_FACTION_QUEST_MIN: Final = 30
REPUTATION_FACTION_QUEST_MAX: Final = 50

OATH_FACTIONS: Final = ("company", "ash_gang")
OATH_CAP: Final = 799  # cap for both without oath, and for the opposing side after an oath
OATH_SWITCH_LOSS: Final = 0.50  # share of current reputation lost at the abandoned faction
OATH_MIN_REPUTATION: Final = 500  # "respected"

ORDER_CAP_CORRUPTION: Final = 50  # from this corruption on, order reputation ...
ORDER_CAP_VALUE: Final = 199  # ... is capped at this value
ASH_GANG_TRUSTED_MIN_CORRUPTION: Final = 25
ASH_GANG_HONORED_MIN_CORRUPTION: Final = 50
ASH_GANG_REP_PER_100_BOUNTY_PER_DAY: Final = 1

HOSTILE_COMPANY_TRAIN_COST_FACTOR: Final = 3
ORDER_RESPECTED_CONFESSION_DISCOUNT: Final = 0.25
KEEPERS_RESPECTED_MAP_ROOM_SPEEDUP: Final = 0.20
KEEPERS_TRUSTED_TRAVEL_REDUCTION: Final = 0.15
KEEPERS_HONORED_RITUAL_CORRUPTION: Final = -25
DUEL_REFUSAL_REPUTATION: Final = -5  # at all factions except keepers

# ---------------------------------------------------------------------------
# Settlement (docs/03-siedlung.md) – base values per building live in content/
# ---------------------------------------------------------------------------

BUILDING_MAX_LEVEL: Final = 10
COST_GROWTH: Final = 1.6
BUILD_TIME_GROWTH: Final = 1.5
BUILD_TIME_REDUCTION_PER_MAIN_HOUSE_LEVEL: Final = 0.03
PRODUCTION_GROWTH: Final = 1.1
STORAGE_BASE: Final = 1000
STORAGE_GROWTH: Final = 1.3
STORAGE_WITHOUT_STOREHOUSE: Final = 500
PROTECTED_BASE: Final = 0.10
PROTECTED_PER_LEVEL: Final = 0.04
PROTECTED_WITHOUT_STOREHOUSE: Final = 0.10
REPAIR_COST_SHARE: Final = 0.25
BUILD_CANCEL_REFUND: Final = 0.50
BUILD_QUEUE_SLOTS: Final = 1
BUILD_QUEUE_SLOTS_EXTENDED: Final = 2
BUILD_QUEUE_EXTENDED_MAIN_HOUSE_LEVEL: Final = 5
SUPERNATURAL_BLACK_ORE_PER_LEVEL: Final = 5
DIG_SITE_BLACK_ORE_MIN_LEVEL: Final = 5

START_RESOURCES: Final[dict[str, int]] = {"wood": 200, "iron": 50}
START_DOLLARS: Final = 150

# Display name of the main house per level (inclusive ranges)
MAIN_HOUSE_NAMES: Final = (
    (1, 1, "tent"),
    (2, 3, "hut"),
    (4, 6, "log_house"),
    (7, 9, "ranch_house"),
    (10, 10, "manor"),
)

SHOOTING_RANGE_TRAINING_REDUCTION_PER_LEVEL: Final = 0.05
APOTHECARY_INJURY_REDUCTION_PER_LEVEL: Final = 0.05
MAP_ROOM_TRAVEL_REDUCTION_PER_LEVEL: Final = 0.02
KENNEL_STOLEN_REDUCTION_PER_LEVEL: Final = 0.03
BONEYARD_MERCHANT_SURCHARGE: Final = 0.10

# ---------------------------------------------------------------------------
# Duels (docs/04-duelle.md, reference: tools/duel_sim.py)
# ---------------------------------------------------------------------------

LIFE_BASE: Final = 40
LIFE_PER_TOUGHNESS: Final = 4
SHOTS_PER_SIDE: Final = 6

HIT_BASE: Final = 50
HIT_PER_POINT: Final = 3
COUNTER_PENALTY: Final = 40
HIT_MIN: Final = 10
HIT_MAX: Final = 90

# zone: (damage, hit modifier %, countered by movement)
ZONES: Final[dict[str, tuple[int, int, str]]] = {
    "head": (30, -15, "duck"),
    "body": (20, 0, "sidestep"),
    "legs": (15, 10, "jump"),
}
MOVES: Final = ("duck", "sidestep", "jump")
LEG_DEBUFF: Final = 15

NERVE_THRESHOLD: Final = 0.30
NERVE_BASE: Final = 40
NERVE_PER_POINT: Final = 2
NERVE_STANDOFF_FACTOR: Final = 2
NERVE_HEADSHOT_THRESHOLD: Final = 10
NERVE_HEADSHOT_PER_POINT: Final = 1

INSTINCT_PER_POINT: Final = 2

BLACK_ORE_BULLET_DAMAGE: Final = 1.25
BLESSING_FACTOR: Final = 0.7
DARK_SIGHT_CORRUPTION: Final = 50
PREACHER_BONUS_VS_CORRUPTED: Final = 1.2
PREACHER_BONUS_CORRUPTION: Final = 50
SHADOW_STEP_CORRUPTION: Final = 75
SHADOW_STEP_PENALTY: Final = 20

FAN_SHOT_PENALTY: Final = 10
FAN_SHOT_THRESHOLD: Final = 0.5
TINCTURE_HEAL: Final = 20
TINCTURE_THRESHOLD: Final = 0.5
DUST_CLOUD_PENALTY: Final = 25
BOUNTY_HUNTER_HIT_BONUS: Final = 10

DUEL_LEVEL_RANGE_MIN: Final = 0.80
DUEL_LEVEL_RANGE_MAX: Final = 1.25
INJURY_HOURS: Final = 2
INJURY_WORK_YIELD_FACTOR: Final = 0.50
DUEL_LOOT_CASH_SHARE: Final = 0.10

BALANCE_TARGET_MIN: Final = 0.45  # design target per class
BALANCE_TARGET_MAX: Final = 0.55
BALANCE_CI_MIN: Final = 0.43  # CI corridor (sampling noise at 2,000 duels)
BALANCE_CI_MAX: Final = 0.57

# ---------------------------------------------------------------------------
# Bounty (docs/05-kopfgeld.md)
# ---------------------------------------------------------------------------

BOUNTY_RAID_PER_LEVEL: Final = 50
BOUNTY_RAID_LOOT_SHARE: Final = 0.25
BOUNTY_RAID_WEAK_VICTIM_LEVEL_SHARE: Final = 0.90
BOUNTY_RAID_WEAK_VICTIM_FACTOR: Final = 2
BOUNTY_CARAVAN_PER_LEVEL: Final = 100
BOUNTY_CORRUPTION_MIN: Final = 75
BOUNTY_CORRUPTION_OFFSET: Final = 70
BOUNTY_CORRUPTION_PER_POINT_PER_DAY: Final = 20
BOUNTY_PRIVATE_MIN: Final = 100
BOUNTY_PRIVATE_RAID_WINDOW_DAYS: Final = 7
BOUNTY_PRIVATE_SHERIFF_FEE: Final = 0.10
BOUNTY_PRIVATE_MIN_ISSUER_LEVEL: Final = 10

# (minimum sum in $, code)
WANTED_TIERS: Final = (
    (1, "wanted"),
    (1000, "dangerous"),
    (5000, "notorious"),
)
DANGEROUS_MERCHANT_SURCHARGE: Final = 0.20

BOUNTY_PAYOUT_HUNTER: Final = 1.0
BOUNTY_PAYOUT_OTHER: Final = 0.5
ARREST_BONUS: Final = 0.25
ARREST_JAIL_HOURS: Final = 2
BOUNTY_ATTEMPTS_PER_TARGET_PER_DAY: Final = 1
BOUNTY_DECAY_PER_DAY: Final = 0.05
BOUNTY_BUYOUT_FACTOR: Final = 1.5
BOUNTY_ORE_DOLLARS_PER_ORE: Final = 50  # proposal in doc, to be balanced
BOUNTY_ORE_REPAYMENT_CORRUPTION: Final = 10
BOUNTY_ORE_REPAYMENT_RESPECTED_DISCOUNT: Final = 0.25
BOUNTY_ABUSE_PAIR_LIMIT: Final = 3  # more than this in the window is logged
BOUNTY_ABUSE_WINDOW_DAYS: Final = 7
BOUNTY_HUNTER_PUSH_MIN: Final = 500
BOUNTY_HUNTER_PUSH_PER_DAY: Final = 3
BOUNTY_HUNTER_WARNING_MINUTES: Final = 10

# ---------------------------------------------------------------------------
# Corruption (docs/06-verderbnis.md) – stored in tenths
# ---------------------------------------------------------------------------

CORRUPTION_SCALE: Final = 10  # tenths per point
CORRUPTION_MAX: Final = 100

# (lower bound inclusive, code)
CORRUPTION_TIERS: Final = (
    (0, "pure"),
    (25, "marked"),
    (50, "tainted"),
    (75, "possessed"),
    (100, "lost"),
)
CORRUPTION_VISIBLE_FROM: Final = 50

ORE_SENSE_BONUS: Final = 0.25
MARKED_MERCHANT_SURCHARGE: Final = 0.10
MARKED_CHAPEL_HEALING_FACTOR: Final = 0.5
POSSESSED_CHARISMA_PENALTY: Final = 3

CORRUPTION_BLACK_ORE_SHOT: Final = 1.0
CORRUPTION_BLACK_ORE_SHOT_ASH_LORD: Final = 0.5
CORRUPTION_ORE_SHRINE: Final = 5
CORRUPTION_WHISPER_WELL: Final = 3
CORRUPTION_ORE_WHISPERS_THRESHOLD: Final = 50  # more than this black ore in storage ...
CORRUPTION_ORE_WHISPERS_PER_DAY: Final = 1  # ... adds this per day

CHAPEL_BASE: Final = 1  # −(1 + level / 2) per day
CHAPEL_PER_LEVEL: Final = 0.5
PREACHER_BLESSING: Final = -5
CONFESSION: Final = -15
CONFESSION_BASE_COST: Final = 200  # × 2^(confessions this week)
CLEANSING_QUEST_MIN: Final = -10
CLEANSING_QUEST_MAX: Final = -25
NATURAL_DECAY_PER_DAY: Final = -1
NATURAL_DECAY_BELOW: Final = 25

WHISPER_AUTO_CHOICE_HOURS: Final = 12

DEPTH_CALLS_HOURS: Final = 24
DEPTH_CALLS_STAT_FACTOR: Final = 1.5
DEPTH_CALLS_LIFE_FACTOR: Final = 3
DEPTH_CALLS_BLACK_ORE_PER_LEVEL: Final = 10
DEPTH_CALLS_RETURN_CORRUPTION: Final = 60
SCARS_MAX: Final = 3

# ---------------------------------------------------------------------------
# Quests (docs/07-auftraege.md)
# ---------------------------------------------------------------------------

CHECK_DIFFICULTIES: Final[dict[str, int]] = {
    "easy": 15,
    "medium": 22,
    "hard": 28,
    "deadly": 35,
}
CHECK_DIE: Final = 20
DAILY_JOBS_PER_FACTION: Final = 3  # daily quests offered per faction and game day
DAILY_JOB_MINUTES_MIN: Final = 15
DAILY_JOB_MINUTES_MAX: Final = 120
TRAIN_HEIST_DIFFICULTY_REDUCTION_PER_ROLE: Final = 5

# Jobs (docs/07-auftraege.md, "Arbeiten") – job list lives in content/jobs.yaml
JOBS_AT_ONCE: Final = 1
JOB_YIELD_PER_LEVEL: Final = 0.10  # yield × (1 + 0.1 × (level − 1)); XP is not scaled

# Resources are stored in thousandths so short production intervals are not lost
RESOURCE_SCALE: Final = 1000

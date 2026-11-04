"""
What a goal leaves in the seed.

Every boss sits at a depth: the number of gates on the way to it (GATE_LEVEL in
rules.py). The goal's depth is that of its deepest boss, and everything is
measured against it:

  - an ordinary stage or town is past the goal once its region sits behind the
    goal's gate or a deeper one -- Sea is past Castle, Hell is past Ice Castle;
  - a boss stage is past the goal once it is deeper than the goal.

Whatever is past the goal is cut: no locations, and no unlock item. A boss at
the goal's own depth that is not a goal (Ice Castle beside a Mountaintop goal),
and any of the three endgame bosses that is not a goal, stays playable but only
ever holds filler.
"""

from __future__ import annotations

from .constants import GOAL_OPTIONS_MAP
from .items import FILLER_TIER, item_table
from .rules import BOSS_GATES, GATE_LEVEL, REGION_LEVEL, SHOP_TIER_GATES
from .shop import ShopLocationDict

# The region each town sits in on the map. Town is where you start and the
# Forget Tree is not a shop, so neither is ever cut.
TOWN_AREAS: dict[str, str] = {
    "Village": "Grassland",
    "Resort": "Desert",
    "Island": "Hell",
}
NEVER_CUT: frozenset[str] = frozenset({"Town", "Forget Tree", "Opening Street"})

# Bosses that are side content whenever they are not the goal.
ENDGAME_BOSSES: frozenset[str] = frozenset({"Hell Castle", "Volcano", "Mountaintop"})

# The highest filler tier for each count of main-chain gates open: tiers 1-2
# drop around Castle, 3 around Submarine Shrine, 4-5 around Pyramid, 6 around
# Ice Castle and 7-8 in Hell.
LOOT_TIER_BY_GATES_OPEN: tuple[int, ...] = (2, 3, 5, 6, 8)

# The boss whose "classes required" option a goal answers to. Mountaintop reads
# Ice Castle's and Volcano Hell Castle's, the same as their gates do.
GOAL_CLASS_OPTION: dict[str, str] = {boss: key for boss, _, _, key in BOSS_GATES}
GOAL_CLASS_OPTION["Volcano"] = "hell_castle"


def loot_tier_cap(gates_open: int) -> int:
    return LOOT_TIER_BY_GATES_OPEN[min(gates_open, len(LOOT_TIER_BY_GATES_OPEN) - 1)]


def stage_level(stage: str) -> int:
    """How deep a stage or town sits; see the module docstring."""
    if stage in GATE_LEVEL:
        return GATE_LEVEL[stage]
    if stage in TOWN_AREAS:
        return REGION_LEVEL[TOWN_AREAS[stage]]
    if stage == "Opening Street":
        return 0
    return REGION_LEVEL[item_table[f"Unlock {stage}"].region]


class GoalScope:
    def __init__(self, goal: int) -> None:
        self.goals: list[str] = GOAL_OPTIONS_MAP[goal]
        self.level: int = max(GATE_LEVEL[name] for name in self.goals)

    def is_cut(self, stage: str) -> bool:
        """Whether a stage or town is past the goal and left out of the seed."""
        if stage in NEVER_CUT:
            return False
        if stage in GATE_LEVEL:
            return GATE_LEVEL[stage] > self.level
        return stage_level(stage) >= self.level

    def is_side_boss(self, stage: str) -> bool:
        """A boss stage that stays playable but whose checks only hold filler."""
        return (
            stage in GATE_LEVEL
            and stage not in self.goals
            and not self.is_cut(stage)
            and (GATE_LEVEL[stage] == self.level or stage in ENDGAME_BOSSES)
        )

    def is_shop_check_cut(self, entry: ShopLocationDict) -> bool:
        """
        A shop check is cut with its town, or when its row is stocked from past
        the goal. The row's boss is the one SHOP_TIER_GATES waits for with
        Progressive Shop on; without it Town stocks the same rows from the same
        stages, so one rule covers both.
        """
        if self.is_cut(entry["region"]):
            return True
        tier = entry.get("tier", 0)
        for threshold, boss_stage in SHOP_TIER_GATES:
            if tier >= threshold:
                return GATE_LEVEL[boss_stage] >= self.level
        return False

    @property
    def loot_tier_cap(self) -> int:
        """The highest filler tier found in the goal's own area."""
        return loot_tier_cap(self.level - 1)

    @property
    def class_options(self) -> list[str]:
        return [f"classes_req_for_{GOAL_CLASS_OPTION[name]}" for name in self.goals]


def filler_within(cap: int) -> list[str]:
    return [name for name, tier in FILLER_TIER.items() if tier <= cap]

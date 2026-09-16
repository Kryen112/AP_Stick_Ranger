"""
Access rules for every stage.

The shape is one gate per boss stage, each chaining off the one before it:

    Castle -> Submarine Shrine -> Pyramid -> Ice Castle -> Hell Castle

A gate opens when you hold that boss stage's own unlock, enough unlocks from the
region in front of it, and enough ranger classes. Ordinary stages in a region
need their own unlock plus the gate of the boss that guards the region.

The client's world map colours stages with the same rules (in_logic() in
game.js). Anything that changes here has to change there too, or the map starts
promising checks Archipelago does not think are reachable.
"""

from __future__ import annotations

from typing import Callable

from BaseClasses import CollectionState, MultiWorld
from worlds.generic.Rules import set_rule

from .constants import RANGER_CLASSES
from .items import PROGRESSIVE_SHOP, unlocks_by_region
from .options import SROptions
from .shop import shop_table

Predicate = Callable[[CollectionState], bool]

# Each region and the boss whose gate it sits behind.
REGION_GATES: tuple[tuple[str, str], ...] = (
    ("Sea", "Castle"),
    ("Desert", "Submarine Shrine"),
    ("Ice", "Pyramid"),
    ("Hell", "Ice Castle"),
)

# Boss stage -> (region counted in front of it, the gate it chains off).
BOSS_GATES: tuple[tuple[str, str, str | None], ...] = (
    ("Castle", "Grassland", None),
    ("Submarine Shrine", "Sea", "Castle"),
    ("Pyramid", "Desert", "Submarine Shrine"),
    ("Ice Castle", "Ice", "Pyramid"),
    ("Hell Castle", "Hell", "Ice Castle"),
)

# Boss rush stages, reachable once the Hell Castle gate is open.
BOSS_RUSH_STAGES: tuple[str, ...] = ("Volcano", "Mountaintop")


def class_count(state: CollectionState, player: int) -> int:
    """
    Number of ranger classes the team has, starting class included.

    The client counts it the same way, and every "classes required" option is
    documented as a total rather than as extra unlocks on top of the start.
    """
    return 1 + sum(state.has(f"Unlock {cls} Class", player) for cls in RANGER_CLASSES)


def boss_gate(
    player: int,
    boss_stage: str,
    region: str,
    previous: Predicate | None,
    required_stages: int,
    required_classes: int,
) -> Predicate:
    """Build the access rule for one boss stage."""
    unlocks = unlocks_by_region[region]

    def rule(
        state: CollectionState,
        _player: int = player,
        _unlock: str = f"Unlock {boss_stage}",
        _unlocks: list[str] = unlocks,
        _previous: Predicate | None = previous,
        _stages: int = required_stages,
        _classes: int = required_classes,
    ) -> bool:
        return (
            (_previous is None or _previous(state))
            and state.has(_unlock, _player)
            and sum(state.has(name, _player) for name in _unlocks) >= _stages
            and class_count(state, _player) >= _classes
        )

    return rule


def set_region_rules(player: int, multiworld: MultiWorld, options: SROptions) -> None:
    """
    Put an access rule on every stage entrance past Opening Street.

    The class requirements are read straight off the options: generate_early has
    already zeroed them when Class Randomizer is off and clamped them so a later
    boss never asks for fewer classes than an earlier one, so what the rules use
    here is exactly what fill_slot_data ships to the client.
    """
    gates: dict[str, Predicate] = {}
    for boss_stage, region, previous in BOSS_GATES:
        key = boss_stage.lower().replace(" ", "_")
        gates[boss_stage] = boss_gate(
            player,
            boss_stage,
            region,
            gates[previous] if previous else None,
            getattr(options, f"stages_req_for_{key}").value,
            getattr(options, f"classes_req_for_{key}").value,
        )
        set_rule(multiworld.get_entrance(boss_stage, player), gates[boss_stage])

    # Volcano and Mountaintop sit behind the Hell Castle gate but still need
    # their own unlock. set_rule replaces whatever create_regions installed, so
    # the unlock has to be repeated here -- without it the fill is free to hide
    # "Unlock Volcano" inside Volcano.
    for boss_stage in BOSS_RUSH_STAGES:
        set_rule(
            multiworld.get_entrance(boss_stage, player),
            lambda state, _pl=player, _nm=f"Unlock {boss_stage}", _gate=gates["Hell Castle"]: (
                state.has(_nm, _pl) and _gate(state)
            ),
        )

    for region, gating_boss in REGION_GATES:
        for unlock_name in unlocks_by_region[region]:
            set_rule(
                multiworld.get_entrance(unlock_name.removeprefix("Unlock "), player),
                lambda state, _pl=player, _nm=unlock_name, _gate=gates[gating_boss]: (
                    state.has(_nm, _pl) and _gate(state)
                ),
            )


def set_shop_rules(player: int, multiworld: MultiWorld, options: SROptions) -> None:
    """
    Gate each shop check on the row it sits in.

    Only meaningful with Progressive Shop on -- otherwise the stock widens as
    stages are beaten, and reaching the town is the whole requirement. Gold is
    never a rule: enemies drop it forever, so any price is reachable.
    """
    if not options.progressive_shop:
        return
    for location_data in shop_table.values():
        tier = location_data.get("tier", 0)
        if not tier:
            continue
        set_rule(
            multiworld.get_location(location_data["name"], player),
            lambda state, _pl=player, _tier=tier: state.has(PROGRESSIVE_SHOP, _pl, _tier),
        )

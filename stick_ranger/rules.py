"""
Access rules for every stage.

The shape is one gate per boss stage, each chaining off the one before it:

    Castle -> Submarine Shrine -> Pyramid -> Ice Castle -> Hell Castle
                                         `-> Mountaintop

Mountaintop sits in the Ice region on the map, so it branches off Pyramid and
asks what Ice Castle asks, bar Ice Castle's own unlock.

A gate opens when you hold that boss stage's own unlock, enough unlocks from the
region in front of it, and enough ranger classes. Ordinary stages in a region
need their own unlock plus the gate of the boss that guards the region.

The web client holds no copy of these rules. logic_description() at the bottom
turns them into data that ships in slot_data, and the client's in_logic()
evaluates that, so a change here reaches the world map through the seed rather
than through a second edit. Only the shape of the description is shared, and
LOGIC_VERSION says which shape this is.
"""

from __future__ import annotations

from typing import Callable

from BaseClasses import CollectionState, MultiWorld
from worlds.generic.Rules import set_rule

from .constants import RANGER_CLASSES
from .items import (
    OPENING_STREET_STAGE_ID,
    PROGRESSIVE_SHOPS,
    stage_id,
    unlocks_by_region,
)
from .options import SROptions
from .regions import regions
from .shop import SHOP_REQS, shop_table

Predicate = Callable[[CollectionState], bool]

# Each region and the boss whose gate it sits behind.
REGION_GATES: tuple[tuple[str, str], ...] = (
    ("Sea", "Castle"),
    ("Desert", "Submarine Shrine"),
    ("Ice", "Pyramid"),
    ("Hell", "Ice Castle"),
)

# Boss stage -> (region counted in front of it, the gate it chains off, the
# boss whose "stages/classes required" options it reads). Mountaintop reads Ice
# Castle's, and comes last so the client's "next gate" reports the main chain.
BOSS_GATES: tuple[tuple[str, str, str | None, str], ...] = (
    ("Castle", "Grassland", None, "castle"),
    ("Submarine Shrine", "Sea", "Castle", "submarine_shrine"),
    ("Pyramid", "Desert", "Submarine Shrine", "pyramid"),
    ("Ice Castle", "Ice", "Pyramid", "ice_castle"),
    ("Hell Castle", "Hell", "Ice Castle", "hell_castle"),
    ("Mountaintop", "Ice", "Pyramid", "ice_castle"),
)

# Boss rush stages, reachable once the Hell Castle gate is open.
BOSS_RUSH_STAGES: tuple[str, ...] = ("Volcano",)

# How deep into the run each boss sits: the number of gates on the way to it,
# its own included. Mountaintop shares Ice Castle's depth and Volcano Hell
# Castle's. A goal's depth decides what is past it; see goal.py.
GATE_LEVEL: dict[str, int] = {}
for _boss, _, _previous, _ in BOSS_GATES:
    GATE_LEVEL[_boss] = 1 + (GATE_LEVEL[_previous] if _previous else 0)
for _boss in BOSS_RUSH_STAGES:
    GATE_LEVEL[_boss] = GATE_LEVEL["Hell Castle"]

# The depth of an ordinary stage: that of the boss whose gate it sits behind,
# and 0 for Grassland, which sits behind none.
REGION_LEVEL: dict[str, int] = {"Grassland": 0}
for _region, _boss in REGION_GATES:
    REGION_LEVEL[_region] = GATE_LEVEL[_boss]

# The main chain, in order, without the Mountaintop branch.
CHAIN_BOSSES: tuple[str, ...] = tuple(
    boss for boss, *_ in BOSS_GATES if boss != "Mountaintop"
)

# Bump this when the shape or meaning of logic_description changes -- a new
# rule type, a field read differently. The client checks it at connect, so a
# rule it does not know how to evaluate is a warning rather than a map that
# quietly promises the wrong stages.
LOGIC_VERSION = 1

# With Progressive Shop on, the game stocks rows by items alone, and logic adds
# a pace on top: a tier is only counted once the world has opened as far as the
# stage that would have stocked it in vanilla (Shop_Reqs in game.js):
#
#     tiers  0-8  Grassland      tiers 18-22  Ice   (behind Pyramid)
#     tiers  9-13 Sea   (behind Castle)      tiers 23-32  Hell  (behind Ice Castle)
#     tiers 14-17 Desert (behind Submarine Shrine)
#
# Without it, the fill was free to hand out nothing but Progressive Shop until
# the shop finally coughed up a stage. Highest threshold first, so the first
# match wins. With Progressive Shop off this table is not used at all.
SHOP_TIER_GATES: tuple[tuple[int, str], ...] = (
    (23, "Ice Castle"),
    (18, "Pyramid"),
    (14, "Submarine Shrine"),
    (9, "Castle"),
)


def shop_tier_gate(tier: int, gates: dict[str, Predicate]) -> Predicate | None:
    """The boss gate a shop tier sits behind, or None for the opening rows."""
    for threshold, boss_stage in SHOP_TIER_GATES:
        if tier >= threshold:
            return gates[boss_stage]
    return None


def region_stage_id(region_name: str) -> int:
    """The game's stage id for a stage region; Opening Street has no unlock item."""
    if region_name == "Opening Street":
        return OPENING_STREET_STAGE_ID
    return stage_id(region_name)


def town_row_stages(row: int) -> list[str]:
    """
    Stages whose clearing stocks Town's row, in the game's own terms.

    Town stocks a row once any beaten stage has a Shop_Reqs entry above it.
    Beating a stage means reaching it, so the rule is "can reach any of these".
    Opening Street's entry is 2, so rows 0 and 1 need nothing.
    """
    return [name for name in regions if SHOP_REQS[region_stage_id(name)] > row]


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


def set_region_rules(
    player: int, multiworld: MultiWorld, options: SROptions
) -> dict[str, Predicate]:
    """
    Put an access rule on every stage entrance past Opening Street.

    The class requirements are read straight off the options: generate_early has
    already zeroed them when Class Randomizer is off and clamped them so a later
    boss never asks for fewer classes than an earlier one, so what the rules use
    here is exactly what fill_slot_data ships to the client.
    """
    gates: dict[str, Predicate] = {}
    for boss_stage, region, previous, key in BOSS_GATES:
        gates[boss_stage] = boss_gate(
            player,
            boss_stage,
            region,
            gates[previous] if previous else None,
            getattr(options, f"stages_req_for_{key}").value,
            getattr(options, f"classes_req_for_{key}").value,
        )
        set_rule(multiworld.get_entrance(boss_stage, player), gates[boss_stage])

    # Volcano sits behind the Hell Castle gate but still needs its own unlock.
    # set_rule replaces whatever create_regions installed, so the unlock has to
    # be repeated here -- without it the fill is free to hide "Unlock Volcano"
    # inside Volcano.
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

    return gates


def set_shop_rules(
    player: int,
    multiworld: MultiWorld,
    options: SROptions,
    gates: dict[str, Predicate],
) -> None:
    """
    Gate each shop check on the row it sits in, the way the game stocks it.

    With Progressive Shop off this is the game's own rule (SHOP_REQS): a Town
    row is stocked once you can beat any stage whose entry is above it, and
    Village, Resort and Island stock everything the moment you can walk in.
    Anything looser strands the seed -- rows 1-8 used to count as free, and a
    third of seeds put a Grassland unlock in a row that needed Castle beaten.

    With Progressive Shop on the game stocks by items alone, so a row needs
    that many of its own shop's Progressive item, and logic also waits for the
    world to open as far as the stage that stocked the row in vanilla
    (SHOP_TIER_GATES) -- stricter than the game, so the fill cannot hand out
    nothing but Progressive Shop until the shop coughs up a stage.

    Gold is never a rule: enemies drop it forever, so any price is reachable.

    Checks the goal cut from the seed have no location to put a rule on.
    """
    present = {location.name for location in multiworld.get_locations(player)}
    for location_data in shop_table.values():
        if location_data["name"] not in present:
            continue
        tier = location_data.get("tier", 0)
        clauses: list[Predicate] = []
        if options.progressive_shop:
            req = location_data.get("req", 0)
            if req:
                clauses.append(
                    lambda state, _pl=player, _req=req, _item=PROGRESSIVE_SHOPS[
                        location_data["region"]
                    ]: state.has(_item, _pl, _req)
                )
            gate = shop_tier_gate(tier, gates)
            if gate is not None:
                clauses.append(gate)
        elif location_data["region"] == "Town":
            stocked_by = town_row_stages(tier)
            if "Opening Street" not in stocked_by:
                clauses.append(
                    lambda state, _pl=player, _stages=tuple(stocked_by): any(
                        state.can_reach_region(name, _pl) for name in _stages
                    )
                )
        if not clauses:
            continue
        set_rule(
            multiworld.get_location(location_data["name"], player),
            lambda state, _clauses=tuple(clauses): all(clause(state) for clause in _clauses),
        )


def logic_description(options: SROptions, goal_level: int) -> dict[str, object]:
    """
    Everything the web client needs to decide what is in logic, as data.

    The client used to carry its own copy of the tables below, which is how the
    two drifted apart six different ways before 1.6.0. Shipping this in
    slot_data instead leaves the client with no logic constants of its own, so
    there is nothing left to drift.

    Every stage is a game stage id, because that is what the client keys on: an
    "Unlock <stage>" item's code minus STAGE_ITEM_OFFSET.

    Gates deeper than the goal are left out. Nothing behind them is in the seed,
    and the client's "what does the next gate need" would otherwise point a
    Castle-goal player at Submarine Shrine once Castle opened.
    """
    gates = []
    for boss_stage, region, previous, key in BOSS_GATES:
        if GATE_LEVEL[boss_stage] > goal_level:
            continue
        gates.append({
            "stage": stage_id(boss_stage),
            "region": region,
            "after": stage_id(previous) if previous else None,
            "stages": getattr(options, f"stages_req_for_{key}").value,
            "classes": getattr(options, f"classes_req_for_{key}").value,
        })

    # Which boss gate each region sits behind. Grassland sits behind nothing --
    # its stages need only their own unlock.
    region_gate: dict[str, int | None] = {region: None for region in unlocks_by_region if region != "Boss"}
    for region, gating_boss in REGION_GATES:
        region_gate[region] = stage_id(gating_boss)

    return {
        "version": LOGIC_VERSION,
        "regions": {
            region: sorted(stage_id(name.removeprefix("Unlock ")) for name in names)
            for region, names in unlocks_by_region.items()
            if region != "Boss"
        },
        "region_gate": region_gate,
        "gates": gates,
        # Volcano needs the Hell Castle gate plus its own unlock.
        "boss_rush": [
            {"stage": stage_id(name), "after": stage_id("Hell Castle")}
            for name in BOSS_RUSH_STAGES
            if GATE_LEVEL[name] <= goal_level
        ],
        # Playable with no unlock item at all. Which stages are towns is map
        # geometry rather than a rule, so the client owns that list itself.
        "free": [OPENING_STREET_STAGE_ID],
        # Shop tier -> the boss gate logic waits for with Progressive Shop on,
        # highest threshold first. Only Enforce Shop Logic acts on this, and
        # only then: with Progressive Shop off the game's own stock table is
        # the rule, so what the shop shows is exactly what logic counts.
        "shop_gates": [
            [threshold, stage_id(boss_stage)] for threshold, boss_stage in SHOP_TIER_GATES
        ],
    }

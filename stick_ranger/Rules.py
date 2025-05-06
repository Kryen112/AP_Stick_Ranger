import random
from worlds.generic.Rules import add_rule, add_item_rule
from .Locations import location_table
from .Regions import region_info, locations_by_region


def _validate_location_consistency():
    """
    Ensure every location in location_table appears in exactly one region,
    and that locations_by_region doesn't reference any names missing from
    location_table.
    """
    flat_names    = set(location_table.keys())
    nested_names  = {loc for locs in locations_by_region.values() for loc in locs}

    missing_in_regions = flat_names - nested_names
    unknown_in_regions = nested_names - flat_names

    errors = []
    if missing_in_regions:
        errors.append(
            "These are in location_table but not in any region:\n  "
            + ", ".join(sorted(missing_in_regions))
        )
    if unknown_in_regions:
        errors.append(
            "These are in locations_by_region but missing from location_table:\n  "
            + ", ".join(sorted(unknown_in_regions))
        )
    if errors:
        raise ValueError("Location consistency check failed:\n" + "\n".join(errors))


def set_rules(self: "StickRanger"):
    _validate_location_consistency()
    world, player = self.multiworld, self.player

    _prevent_self_unlock(world, player)
    _restrict_stage_access(world, player)
    _restrict_region_access(world, player) 
    _gate_exit_after_n_stages(world, player, min_stages=5, max_stages=10)


def _prevent_self_unlock(world, player):
    """
    Prevent any "Unlock X" progression item from being placed at X or X Book.
    """
    for _, locs in locations_by_region.items():
        for loc_name in locs:
            loc = world.get_location(loc_name, player)
            base = loc_name.replace(" Book", "")
            def no_self(item, _base=base):
                return item.name != f"Unlock {_base}"
            add_item_rule(loc, no_self)


def _restrict_stage_access(world, player):
    """
    For each stage X (except Opening Street), require "Unlock X" before
    you can play/check location X or X Book.
    """
    default_free = {"Opening Street"}

    for _, locs in locations_by_region.items():
        for loc_name in locs:
            base = loc_name.replace(" Book", "")
            if base in default_free:
                continue
            loc   = world.get_location(loc_name, player)
            need  = f"Unlock {base}"
            add_rule(loc, lambda st, req=need: st.has(req, player))


def _restrict_region_access(world, player):
    """
    For each mandatory connection (Exit → Region), require the matching
    "Unlock Exit" before *any* location in that Region becomes reachable.
    """
    for exit_name, region_name in region_info["mandatory_connections"]:
        # skip the New Game → Grassland start
        if exit_name == "New Game":
            continue
        must_have = f"Unlock {exit_name}"
        for loc_name in locations_by_region.get(region_name, []):
            loc = world.get_location(loc_name, player)
            # every check (stage or book) in region_name now also needs must_have
            add_rule(loc, lambda st, req=must_have: st.has(req, player))

def _gate_exit_after_n_stages(world, player, min_stages=5, max_stages=10):
    """
    For each region-end exit X (e.g. Castle, Submarine Shrine, ...):
      • Choose N in [min_stages, max_stages].
      • Randomly pick N distinct normal stages from X's region.
      • Add_rule on the entrance X so you need Unlock X *and*
        all Unlock <stage_i> for those N stages.
    """
    # build quick lookup of entrance objects
    entrances = {
        exit_name: world.get_entrance(exit_name, player)
        for _, exits in region_info["regions"]
        for exit_name in exits
        if exit_name != "New Game"
    }

    for exit_name, home_region in {
        exit_name: region_name
        for region_name, exits in region_info["regions"]
        for exit_name in exits
        if exit_name != "New Game"
    }.items():
        ent = entrances[exit_name]
        # all real stages (no " Book", not the exit itself)
        pool = [
            loc for loc in locations_by_region[home_region]
            if not loc.endswith(" Book") and loc != exit_name
        ]
        # if there are fewer than min_stages, just require them all
        N = min(len(pool), random.randint(min_stages, max_stages))
        chosen = random.sample(pool, N)

        def make_rule(required_stages):
            def rule(state):
                # must have the exit‐key itself
                if not state.has(f"Unlock {exit_name}", player):
                    return False
                # must have all the chosen stage-unlocks
                return all(
                    state.has(f"Unlock {stage}", player)
                    for stage in required_stages
                )
            return rule

        add_rule(ent, make_rule(chosen))
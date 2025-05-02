from worlds.generic.Rules import add_rule, add_item_rule
from .Locations import location_table
from .Regions import region_info, locations_by_region

def set_rules(self: "StickRanger"):
    world  = self.multiworld
    player = self.player

    for region_name, exits in region_info["regions"]:
        for exit_name in exits:
            if exit_name == "New Game":
                continue
            entrance = world.get_entrance(exit_name, player)
            add_rule(entrance, lambda st, e=exit_name: st.has(f"Unlock {e}", player))

    target_to_region = {}
    for region, locs in locations_by_region.items():
        for loc in locs:
            target_to_region[loc] = region

    for region, locs in locations_by_region.items():
        for loc_name in locs:
            loc = world.get_location(loc_name, player)
            def placement_rule(item, region=region):
                if not item.name.startswith("Unlock "):
                    return True
                target = item.name[len("Unlock "):]
                return target_to_region.get(target) == region
            add_item_rule(loc, placement_rule)
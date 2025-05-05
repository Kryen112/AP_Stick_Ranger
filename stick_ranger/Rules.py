from worlds.generic.Rules import add_rule, add_item_rule
from .Items import item_table
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
        for stage_location in locs:
            target_to_region[stage_location] = region

    # for region, locs in locations_by_region.items():
    #     for loc_name in locs:
    #         stage_location = world.get_location(loc_name, player)
    #         def placement_rule(item, region=region):
    #             if not item.name.startswith("Unlock "):
    #                 return True
    #             target = item.name[len("Unlock "):]
    #             return target_to_region.get(target) == region
    #         add_item_rule(stage_location, placement_rule)

#     region_connections = get_region_connections(player)
#     for region_name, data in region_connections.items():
#         region = self.multiworld.get_region(region_name, player)
#         for location in region.locations:
#             location.access_rule = data["access_rule"]

# def get_region_connections(player):
#     region_connections = {}
#     for location_name in location_table:
#         if "Book" in location_name and "Opening Street" not in location_name:
#             stage = location_name.replace(" Book", "")
#             unlock_item = f"Unlock {stage}"
#             region_connections.setdefault(stage, {
#                 "access_rule": lambda state, unlock_item=unlock_item, p=player: state.has(unlock_item, p),
#                 "locations": [
#                     stage,
#                     location_name
#                 ]
#             })
#             region_connections[stage]["locations"].append(location_name)
#     return region_connections

    
    for location_name in location_table:
        if "Book" in location_name:
            stage_name = location_name.replace(" Book", "")
            unlock_item = f"Unlock {stage_name}"
            
            stage_location = world.get_location(stage_name, player)
            book_location = world.get_location(location_name, player)
            
            stage_location.access_rule = lambda state, unlock_item=unlock_item, p=player: state.has(unlock_item, p)
            book_location.access_rule = lambda state, unlock_item=unlock_item, p=player: state.has(unlock_item, p)


#     stage_connections = get_stage_connections()
#     print(stage_connections)
#     for unlock_item, stages in stage_connections:
#         for stage in stages:
#             stage.access_rule = lambda state, unlock_item=unlock_item, p=player: state.has(unlock_item, p)

# def get_stage_connections():
#     stage_connections = {}
#     for location_name in location_table:
#         if "Book" in location_name and "Opening Street" not in location_name:
#             stage = location_name.replace(" Book", "")
#             unlock_item = f"Unlock {stage}"
#             stage_connections[unlock_item] = [stage, location_name]
#     return stage_connections
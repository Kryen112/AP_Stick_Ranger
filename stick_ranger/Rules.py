import random
from worlds.generic.Rules import add_rule, add_item_rule, set_rule
from .Locations import location_table
from .Regions import regions

CASTLE_THRESHOLD = random.randint(5, 10)
def set_rules(self: "StickRanger"):
    world, player = self.multiworld, self.player

    # _prevent_self_unlock(world, player)
    # _restrict_stage_access(world, player)
    # _restrict_region_access(world, player) 
    # _gate_exit_after_n_stages(world, player, min_stages=5, max_stages=10)
    set_region_rules(player, world)


# def _prevent_self_unlock(world, player):
#     """
#     Prevent any "Unlock X" progression item from being placed at X or X Book.
#     """
#     for _, locs in regions.items():
#         for loc_name in locs:
#             loc = world.get_location(loc_name, player)
#             base = loc_name.replace(" Book", "")
#             def no_self(item, _base=base):
#                 return item.name != f"Unlock {_base}"
#             add_item_rule(loc, no_self)


# def _restrict_stage_access(world, player):
#     """
#     For each stage X (except Opening Street), require "Unlock X" before
#     you can play/check location X or X Book.
#     """
#     default_free = {"Opening Street"}

#     for _, locs in regions.items():
#         for loc_name in locs:
#             base = loc_name.replace(" Book", "")
#             if base in default_free:
#                 continue
#             loc   = world.get_location(loc_name, player)
#             need  = f"Unlock {base}"
#             add_rule(loc, lambda st, req=need: st.has(req, player))


# def _restrict_region_access(world, player):
#     """
#     For each mandatory connection (Exit → Region), require the matching
#     "Unlock Exit" before *any* location in that Region becomes reachable.
#     """
#     for exit_name, region_name in region_info["mandatory_connections"]:
#         # skip the New Game → Grassland start
#         if exit_name == "New Game":
#             continue
#         must_have = f"Unlock {exit_name}"
#         for loc_name in regions.get(region_name, []):
#             loc = world.get_location(loc_name, player)
#             # every check (stage or book) in region_name now also needs must_have
#             add_rule(loc, lambda st, req=must_have: st.has(req, player))

# def _gate_exit_after_n_stages(world, player, min_stages=5, max_stages=10):
#     """
#     For each region-end exit X (e.g. Castle, Submarine Shrine, ...):
#       • Choose N in [min_stages, max_stages].
#       • Randomly pick N distinct normal stages from X's region.
#       • Add_rule on the entrance X so you need Unlock X *and*
#         all Unlock <stage_i> for those N stages.
#     """
#     # build quick lookup of entrance objects
#     entrances = {
#         exit_name: world.get_entrance(exit_name, player)
#         for _, exits in region_info["regions"]
#         for exit_name in exits
#         if exit_name != "New Game"
#     }

#     for exit_name, home_region in {
#         exit_name: region_name
#         for region_name, exits in region_info["regions"]
#         for exit_name in exits
#         if exit_name != "New Game"
#     }.items():
#         ent = entrances[exit_name]
#         # all real stages (no " Book", not the exit itself)
#         pool = [
#             loc for loc in regions[home_region]
#             if not loc.endswith(" Book") and loc != exit_name
#         ]
#         # if there are fewer than min_stages, just require them all
#         N = min(len(pool), random.randint(min_stages, max_stages))
#         chosen = random.sample(pool, N)

#         def make_rule(required_stages):
#             def rule(state):
#                 # must have the exit‐key itself
#                 if not state.has(f"Unlock {exit_name}", player):
#                     return False
#                 # must have all the chosen stage-unlocks
#                 return all(
#                     state.has(f"Unlock {stage}", player)
#                     for stage in required_stages
#                 )
#             return rule

#         add_rule(ent, make_rule(chosen))

def set_region_rules(player, multiworld):
    set_rule(multiworld.get_entrance("Grassland 1", player), lambda state:
        state.has("Unlock Grassland 1", player, 1))
    set_rule(multiworld.get_entrance("Grassland 2", player), lambda state:
        state.has("Unlock Grassland 2", player, 1))
    set_rule(multiworld.get_entrance("Grassland 3", player), lambda state:
        state.has("Unlock Grassland 3", player, 1))
    set_rule(multiworld.get_entrance("Grassland 4", player), lambda state:
        state.has("Unlock Grassland 4", player, 1))
    set_rule(multiworld.get_entrance("Grassland 5", player), lambda state:
        state.has("Unlock Grassland 5", player, 1))
    set_rule(multiworld.get_entrance("Grassland 6", player), lambda state:
        state.has("Unlock Grassland 6", player, 1))
    set_rule(multiworld.get_entrance("Grassland 7", player), lambda state:
        state.has("Unlock Grassland 7", player, 1))
    set_rule(multiworld.get_entrance("Castle Gate", player), lambda state:
        state.has("Unlock Castle Gate", player, 1))
    set_rule(multiworld.get_entrance("Castle", player), lambda state, T=random.randint(5, 10): # TODO do this for other stages
        state.has("Unlock Castle", player, 1) and 
        sum(1 for key in [
                    "Unlock Grassland 1",
                    "Unlock Grassland 2",
                    "Unlock Grassland 3",
                    "Unlock Grassland 4",
                    "Unlock Grassland 5",
                    "Unlock Grassland 6",
                    "Unlock Grassland 7",
                    "Unlock Lake",
                    "Unlock Hill Country 1",
                    "Unlock Hill Country 2",
                    "Unlock Hill Country 3",
                    "Unlock Forest 1",
                    "Unlock Forest 2",
                    "Unlock Cavern 1",
                    "Unlock Cavern 2",
                    "Unlock Cavern 3",
                    "Unlock Castle Gate",
                ] if state.has(key, player, 1)
            ) >= T)
    set_rule(multiworld.get_entrance("Hill Country 1", player), lambda state:
        state.has("Unlock Hill Country 1", player, 1))
    set_rule(multiworld.get_entrance("Hill Country 2", player), lambda state:
        state.has("Unlock Hill Country 2", player, 1))
    set_rule(multiworld.get_entrance("Hill Country 3", player), lambda state:
        state.has("Unlock Hill Country 3", player, 1))
    set_rule(multiworld.get_entrance("Lake", player), lambda state:
        state.has("Unlock Lake", player, 1))
    set_rule(multiworld.get_entrance("Forest 1", player), lambda state:
        state.has("Unlock Forest 1", player, 1))
    set_rule(multiworld.get_entrance("Forest 2", player), lambda state:
        state.has("Unlock Forest 2", player, 1))
    set_rule(multiworld.get_entrance("Cavern 1", player), lambda state:
        state.has("Unlock Cavern 1", player, 1))
    set_rule(multiworld.get_entrance("Cavern 2", player), lambda state:
        state.has("Unlock Cavern 2", player, 1))
    set_rule(multiworld.get_entrance("Cavern 3", player), lambda state:
        state.has("Unlock Cavern 3", player, 1))
    set_rule(multiworld.get_entrance("Seaside 1", player), lambda state:
        state.has("Unlock Seaside 1", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Seaside 2", player), lambda state:
        state.has("Unlock Seaside 2", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Seaside 3", player), lambda state:
        state.has("Unlock Seaside 3", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Seaside 4", player), lambda state:
        state.has("Unlock Seaside 4", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Submarine 1", player), lambda state:
        state.has("Unlock Submarine 1", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Submarine 2", player), lambda state:
        state.has("Unlock Submarine 2", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Submarine 3", player), lambda state:
        state.has("Unlock Submarine 3", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Submarine 4", player), lambda state:
        state.has("Unlock Submarine 4", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Submarine Shrine", player), lambda state:
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Mist Grove 1", player), lambda state:
        state.has("Unlock Mist Grove 1", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Mist Grove 2", player), lambda state:
        state.has("Unlock Mist Grove 2", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Mist Grove 3", player), lambda state:
        state.has("Unlock Mist Grove 3", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("???", player), lambda state:
        state.has("Unlock ???", player, 1) and
        state.has("Unlock Castle", player, 1))
    set_rule(multiworld.get_entrance("Desert 1", player), lambda state:
        state.has("Unlock Desert 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 2", player), lambda state:
        state.has("Unlock Desert 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 3", player), lambda state:
        state.has("Unlock Desert 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 4", player), lambda state:
        state.has("Unlock Desert 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 5", player), lambda state:
        state.has("Unlock Desert 5", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Oasis", player), lambda state:
        state.has("Unlock Oasis", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 6", player), lambda state:
        state.has("Unlock Desert 6", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 7", player), lambda state:
        state.has("Unlock Desert 7", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Pyramid", player), lambda state:
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Desert 8", player), lambda state:
        state.has("Unlock Desert 8", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Beach 1", player), lambda state:
        state.has("Unlock Beach 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Beach 2", player), lambda state:
        state.has("Unlock Beach 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Beach 3", player), lambda state:
        state.has("Unlock Beach 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1))
    set_rule(multiworld.get_entrance("Cavern 4", player), lambda state:
        state.has("Unlock Cavern 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Cavern 5", player), lambda state:
        state.has("Unlock Cavern 5", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Cavern 6", player), lambda state:
        state.has("Unlock Cavern 6", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 1", player), lambda state:
        state.has("Unlock Snowfield 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 2", player), lambda state:
        state.has("Unlock Snowfield 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Mountain 1", player), lambda state:
        state.has("Unlock Mountain 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Mountain 2", player), lambda state:
        state.has("Unlock Mountain 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Mountaintop", player), lambda state:
        state.has("Unlock Mountaintop", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 3", player), lambda state:
        state.has("Unlock Snowfield 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 4", player), lambda state:
        state.has("Unlock Snowfield 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 5", player), lambda state:
        state.has("Unlock Snowfield 5", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 6", player), lambda state:
        state.has("Unlock Snowfield 6", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 7", player), lambda state:
        state.has("Unlock Snowfield 7", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 8", player), lambda state:
        state.has("Unlock Snowfield 8", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Frozen Lake", player), lambda state:
        state.has("Unlock Frozen Lake", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Ice Castle", player), lambda state:
        state.has("Unlock Ice Castle", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1))
    set_rule(multiworld.get_entrance("Snowfield 9", player), lambda state:
        state.has("Unlock Snowfield 9", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Beach 4", player), lambda state:
        state.has("Unlock Beach 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Forest 3", player), lambda state:
        state.has("Unlock Forest 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Forest 4", player), lambda state:
        state.has("Unlock Forest 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Forest 5", player), lambda state:
        state.has("Unlock Forest 5", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Forest 6", player), lambda state:
        state.has("Unlock Forest 6", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("!!!", player), lambda state:
        state.has("Unlock !!!", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 1", player), lambda state:
        state.has("Unlock Hell 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 2", player), lambda state:
        state.has("Unlock Hell 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 3", player), lambda state:
        state.has("Unlock Hell 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 4", player), lambda state:
        state.has("Unlock Hell 4", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 5", player), lambda state:
        state.has("Unlock Hell 5", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 6", player), lambda state:
        state.has("Unlock Hell 6", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Inferno 1", player), lambda state:
        state.has("Unlock Inferno 1", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Inferno 2", player), lambda state:
        state.has("Unlock Inferno 2", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Inferno 3", player), lambda state:
        state.has("Unlock Inferno 3", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Blood Lake", player), lambda state:
        state.has("Unlock Blood Lake", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Cavern 7", player), lambda state:
        state.has("Unlock Cavern 7", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Cavern 8", player), lambda state:
        state.has("Unlock Cavern 8", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 7", player), lambda state:
        state.has("Unlock Hell 7", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell 8", player), lambda state:
        state.has("Unlock Hell 8", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell Gate", player), lambda state:
        state.has("Unlock Hell Gate", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Hell Castle", player), lambda state:
        state.has("Unlock Hell Castle", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
    set_rule(multiworld.get_entrance("Volcano", player), lambda state:
        state.has("Unlock Volcano", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
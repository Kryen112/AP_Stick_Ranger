import random
from worlds.generic.Rules import set_rule

def set_rules(self: "StickRanger"):
    set_region_rules(self.player, self.multiworld)


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
    set_rule(multiworld.get_entrance("Castle", player), lambda state, T=random.randint(6, 17):
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
    set_rule(multiworld.get_entrance("Submarine Shrine", player), lambda state, T=random.randint(4, 12):
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Castle", player, 1) and 
        sum(1 for key in [
                    "Unlock Seaside 1",
                    "Unlock Seaside 2",
                    "Unlock Seaside 3",
                    "Unlock Seaside 4",
                    "Unlock Submarine 1",
                    "Unlock Submarine 2",
                    "Unlock Submarine 3",
                    "Unlock Submarine 4",
                    "Unlock Mist Grove 1",
                    "Unlock Mist Grove 2",
                    "Unlock Mist Grove 3",
                    "???",
                ] if state.has(key, player, 1)
            ) >= T)
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
    set_rule(multiworld.get_entrance("Pyramid", player), lambda state, T=random.randint(4, 12):
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and 
        sum(1 for key in [
                    "Unlock Desert 1",
                    "Unlock Desert 2",
                    "Unlock Desert 3",
                    "Unlock Desert 4",
                    "Unlock Desert 5",
                    "Unlock Oasis",
                    "Unlock Desert 6",
                    "Unlock Desert 7",
                    "Unlock Desert 8",
                    "Unlock Beach 1",
                    "Unlock Beach 2",
                    "Unlock Beach 3",
                ] if state.has(key, player, 1)
            ) >= T)
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
    set_rule(multiworld.get_entrance("Ice Castle", player), lambda state, T=random.randint(5, 14):
        state.has("Unlock Ice Castle", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and 
        sum(1 for key in [
                    "Unlock Cavern 4",
                    "Unlock Cavern 5",
                    "Unlock Cavern 6",
                    "Unlock Snowfield 1",
                    "Unlock Snowfield 2",
                    "Unlock Mountain 1",
                    "Unlock Mountain 2",
                    # "Unlock Mountaintop", too difficult
                    "Unlock Snowfield 3",
                    "Unlock Snowfield 4",
                    "Unlock Snowfield 5",
                    "Unlock Snowfield 6",
                    "Unlock Snowfield 7",
                    "Unlock Snowfield 8",
                    "Unlock Frozen Lake",
                ] if state.has(key, player, 1)
            ) >= T)
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
    set_rule(multiworld.get_entrance("Hell Castle", player), lambda state, T=random.randint(7, 23):
        state.has("Unlock Hell Castle", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1) and 
        sum(1 for key in [
                    "Unlock Snowfield 9",
                    "Unlock Beach 4",
                    "Unlock Forest 3",
                    "Unlock Forest 4",
                    "Unlock Forest 5",
                    "Unlock Forest 6",
                    "Unlock !!!",
                    "Unlock Hell 1",
                    "Unlock Hell 2",
                    "Unlock Hell 3",
                    "Unlock Hell 4",
                    "Unlock Hell 5",
                    "Unlock Hell 6",
                    "Unlock Inferno 1",
                    "Unlock Inferno 2",
                    "Unlock Inferno 3",
                    "Unlock Blood Lake",
                    "Unlock Cavern 7",
                    "Unlock Cavern 8",
                    "Unlock Hell 7",
                    "Unlock Hell 8",
                    "Unlock Hell Gate",
                    # "Unlock Volcano", too difficult
                ] if state.has(key, player, 1)
            ) >= T)
    set_rule(multiworld.get_entrance("Volcano", player), lambda state:
        state.has("Unlock Volcano", player, 1) and
        state.has("Unlock Castle", player, 1) and
        state.has("Unlock Submarine Shrine", player, 1) and
        state.has("Unlock Pyramid", player, 1) and
        state.has("Unlock Ice Castle", player, 1))
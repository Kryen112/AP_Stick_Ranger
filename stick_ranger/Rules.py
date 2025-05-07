from random import randint
from worlds.generic.Rules import set_rule
from .Items import unlocks_by_region

def set_rules(self: "StickRanger"):
    set_region_rules(self.player, self.multiworld)

def set_region_rules(player, multiworld):
    castle_predicate = reached_castle(player)
    set_rule(multiworld.get_entrance("Castle", player), castle_predicate)

    submarine_shrine_predicate = reached_submarine_shrine(player, castle_predicate)
    set_rule(multiworld.get_entrance("Submarine Shrine", player), submarine_shrine_predicate)

    pyramid_predicate = reached_pyramid(player, submarine_shrine_predicate)
    set_rule(multiworld.get_entrance("Pyramid", player), pyramid_predicate)

    ice_castle_predicate = reached_ice_castle(player, pyramid_predicate)
    set_rule(multiworld.get_entrance("Ice Castle", player), ice_castle_predicate)

    hell_castle_predicate = reached_hell_castle(player, ice_castle_predicate)
    set_rule(multiworld.get_entrance("Hell Castle", player), hell_castle_predicate)

    for unlock_name in unlocks_by_region["Sea"]:
        entrance_name = multiworld.get_entrance(unlock_name.replace("Unlock ", ""), player)
        set_rule(entrance_name, lambda state, _pl=player, _nm=unlock_name, _c=castle_predicate:
            state.has(_nm, _pl, 1) and _c(state)
        )

    for unlock_name in unlocks_by_region["Desert"]:
        entrance_name = multiworld.get_entrance(unlock_name.replace("Unlock ", ""), player)
        set_rule(entrance_name, lambda state, _pl=player, _nm=unlock_name, _s=submarine_shrine_predicate:
            state.has(_nm, _pl, 1) and _s(state)
        )

    for unlock_name in unlocks_by_region["Ice"]:
        entrance_name = multiworld.get_entrance(unlock_name.replace("Unlock ", ""), player)
        set_rule(entrance_name, lambda state, _pl=player, _nm=unlock_name, _p=pyramid_predicate:
            state.has(_nm, _pl, 1) and _p(state)
        )

    for unlock_name in unlocks_by_region["Hell"]:
        entrance_name = multiworld.get_entrance(unlock_name.replace("Unlock ", ""), player)
        set_rule(entrance_name, lambda state, _pl=player, _nm=unlock_name, _i=ice_castle_predicate:
            state.has(_nm, _pl, 1) and _i(state)
        )

def reached_castle(player):
    return lambda state, _pl=player, _T=randint(6, 10), _keys=unlocks_by_region["Grassland"]: (
        state.has("Unlock Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
    )

def reached_submarine_shrine(player, castle_pred):
    return lambda state, _pl=player, _T=randint(4, 7), _keys=unlocks_by_region["Sea"], _c=castle_pred: (
        _c(state)
        and state.has("Unlock Submarine Shrine", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
    )

def reached_pyramid(player, submarine_shrine_pred):
    return lambda state, _pl=player, _T=randint(4, 7), _keys=unlocks_by_region["Desert"], _s=submarine_shrine_pred: (
        _s(state)
        and state.has("Unlock Pyramid", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
    )

def reached_ice_castle(player, pyramid_pred):
    return lambda state, _pl=player, _T=randint(5, 8), _keys=unlocks_by_region["Ice"], _p=pyramid_pred: (
        _p(state)
        and state.has("Unlock Ice Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
    )

def reached_hell_castle(player, ice_castle_pred):
    return lambda state, _pl=player, _T=randint(6, 10), _keys=unlocks_by_region["Hell"], _i=ice_castle_pred: (
        _i(state)
        and state.has("Unlock Hell Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
    )
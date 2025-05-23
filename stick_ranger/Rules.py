from worlds.generic.Rules import set_rule
from .Items import unlocks_by_region

RANGER_CLASSES = [
    "Boxer",
    "Gladiator",
    "Sniper",
    "Magician",
    "Priest",
    "Gunner",
    "Whipper",
    "Angel"
]

def class_count(state, player):
    """Return the number of ranger classes the player has unlocked."""
    return sum(
        state.has(f"Unlock {cls} Class", player)
        for cls in RANGER_CLASSES
    )

def set_rules(self: "StickRanger"):
    options = self.options
    boss_stage_reqs = {
        "Castle": options.classes_req_for_castle.value,
        "Submarine Shrine": options.classes_req_for_submarine_shrine.value,
        "Pyramid": options.classes_req_for_pyramid.value,
        "Ice Castle": options.classes_req_for_ice_castle.value,
        "Hell Castle": options.classes_req_for_hell_castle.value,
    }

    if not options.ranger_class_randomizer.value:
        for stage in boss_stage_reqs:
            boss_stage_reqs[stage] = 0

    order = ["Castle", "Submarine Shrine", "Pyramid", "Ice Castle", "Hell Castle"]
    for prev, nxt in zip(order, order[1:]):
        boss_stage_reqs[nxt] = max(boss_stage_reqs[prev], boss_stage_reqs[nxt])

    set_region_rules(self.player, self.multiworld, boss_stage_reqs)

def set_region_rules(player, multiworld, boss_stage_reqs):
    castle_predicate = reached_castle(player, multiworld.random.randint(6, 10), boss_stage_reqs["Castle"])
    set_rule(multiworld.get_entrance("Castle", player), castle_predicate)

    submarine_shrine_predicate = reached_submarine_shrine(player, castle_predicate, multiworld.random.randint(4, 7), boss_stage_reqs["Submarine Shrine"])
    set_rule(multiworld.get_entrance("Submarine Shrine", player), submarine_shrine_predicate)

    pyramid_predicate = reached_pyramid(player, submarine_shrine_predicate, multiworld.random.randint(4, 7), boss_stage_reqs["Pyramid"])
    set_rule(multiworld.get_entrance("Pyramid", player), pyramid_predicate)

    ice_castle_predicate = reached_ice_castle(player, pyramid_predicate, multiworld.random.randint(5, 8), boss_stage_reqs["Ice Castle"])
    set_rule(multiworld.get_entrance("Ice Castle", player), ice_castle_predicate)

    hell_castle_predicate = reached_hell_castle(player, ice_castle_predicate, multiworld.random.randint(6, 10), boss_stage_reqs["Hell Castle"])
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


def reached_castle(player, threshold, req_classes):
    return lambda state, _pl=player, _T=threshold, _keys=unlocks_by_region["Grassland"]: (
        state.has("Unlock Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
        and class_count(state, _pl) >= req_classes
    )

def reached_submarine_shrine(player, castle_pred, threshold, req_classes):
    return lambda state, _pl=player, _T=threshold, _keys=unlocks_by_region["Sea"], _c=castle_pred: (
        _c(state)
        and state.has("Unlock Submarine Shrine", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
        and class_count(state, _pl) >= req_classes
    )

def reached_pyramid(player, submarine_shrine_pred, threshold, req_classes):
    return lambda state, _pl=player, _T=threshold, _keys=unlocks_by_region["Desert"], _s=submarine_shrine_pred: (
        _s(state)
        and state.has("Unlock Pyramid", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
        and class_count(state, _pl) >= req_classes
    )

def reached_ice_castle(player, pyramid_pred, threshold, req_classes):
    return lambda state, _pl=player, _T=threshold, _keys=unlocks_by_region["Ice"], _p=pyramid_pred: (
        _p(state)
        and state.has("Unlock Ice Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
        and class_count(state, _pl) >= req_classes
    )

def reached_hell_castle(player, ice_castle_pred, threshold, req_classes):
    return lambda state, _pl=player, _T=threshold, _keys=unlocks_by_region["Hell"], _i=ice_castle_pred: (
        _i(state)
        and state.has("Unlock Hell Castle", _pl, 1)
        and sum(1 for k in _keys if state.has(k, _pl, 1)) >= _T
        and class_count(state, _pl) >= req_classes
    )
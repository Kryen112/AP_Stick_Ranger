from __future__ import annotations


STAGE_SETTINGS: list[tuple[str, str, str, str]] = [
    (
        "castle",
        "min_stages_req_for_castle",
        "max_stages_req_for_castle",
        "stages_req_for_castle",
    ),
    (
        "submarine_shrine",
        "min_stages_req_for_submarine_shrine",
        "max_stages_req_for_submarine_shrine",
        "stages_req_for_submarine_shrine",
    ),
    (
        "pyramid",
        "min_stages_req_for_pyramid",
        "max_stages_req_for_pyramid",
        "stages_req_for_pyramid",
    ),
    (
        "ice_castle",
        "min_stages_req_for_ice_castle",
        "max_stages_req_for_ice_castle",
        "stages_req_for_ice_castle",
    ),
    (
        "hell_castle",
        "min_stages_req_for_hell_castle",
        "max_stages_req_for_hell_castle",
        "stages_req_for_hell_castle",
    ),
]

# Boss gates in progression order. generate_early clamps these so a later boss
# never asks for fewer classes than an earlier one, and zeroes them all when
# Class Randomizer is off -- fill_slot_data then ships the resolved values, so
# the in-game logic display gates on the same numbers the rules do.
CLASS_REQ_OPTIONS: list[str] = [
    "classes_req_for_castle",
    "classes_req_for_submarine_shrine",
    "classes_req_for_pyramid",
    "classes_req_for_ice_castle",
    "classes_req_for_hell_castle",
]

ENEMIES_OPTION_NON_BOSS: int = 1
ENEMIES_OPTION_BOSS: int = 2
ENEMIES_OPTION_ALL: int = 3

# Share of the filler budget that becomes Traps, per Traps option value. The
# old scale was a flat 25% per step, which made the lowest setting rougher than
# anyone wanted.
TRAP_SHARE_BY_OPTION: dict[int, int] = {0: 0, 1: 5, 2: 10, 3: 20, 4: 50, 5: 100}

STARTER_UNLOCK_CHOICES: list[str] = [
    "Unlock Grassland 1",
    "Unlock Grassland 2",
    "Unlock Grassland 3",
    "Unlock Grassland 4",
    "Unlock Hill Country 1",
]

OPENING_STREET_EXIT: str = "Opening Street: Exit"
OPENING_STREET_BOOK: str = "Opening Street: Book"
OPENING_STREET_ENEMIES: list[str] = [
    "Opening Street: Green Smiley Walker",
    "Opening Street: Cyan Smiley Walker",
    "Opening Street: Red Smiley Walker",
    "Opening Street: Blue X Walker",
]
OPENING_STREET_BOSS: str = "Opening Street: Grey Boss Smiley Walker"

RANGER_CLASSES: list[str] = [
    "Boxer",
    "Gladiator",
    "Sniper",
    "Magician",
    "Priest",
    "Gunner",
    "Whipper",
    "Angel",
]

GOAL_LOCATIONS: dict[str, list[str]] = {
    "Volcano": ["Volcano: Exit", "Volcano: Book", "Volcano: Yellow Boss Box Eel"],
    "Mountaintop": [
        "Mountaintop: Exit",
        "Mountaintop: Book",
        "Mountaintop: Red Boss Smiley Eel",
        "Mountaintop: Blue Boss Fairy Eel",
        "Mountaintop: Olive Boss Star Eel",
        "Mountaintop: Green Boss Cap Eel",
    ],
    "Hell Castle": [
        "Hell Castle: Exit",
        "Hell Castle: Book",
        "Hell Castle: Hell Castle Boss",
    ],
}

GOAL_OPTIONS_MAP: dict[int, list[str]] = {
    0: ["Hell Castle"],
    1: ["Volcano"],
    2: ["Mountaintop"],
    3: ["Hell Castle", "Volcano"],
    4: ["Hell Castle", "Mountaintop"],
    5: ["Volcano", "Mountaintop"],
    6: ["Hell Castle", "Volcano", "Mountaintop"],
}

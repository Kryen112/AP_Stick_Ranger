from BaseClasses import Region, Entrance
from worlds.AutoWorld import World
from Options import OptionError
from .Items import SRItem, item_table, stages, filler, traps
from .Locations import SRLocation, stages_table, books_table, enemies_table, location_name_to_id
from .Options import SROptions
from .Regions import regions
from .Rules import set_rules


ENEMIES_NORMAL = 1
ENEMIES_BOSS = 2
ENEMIES_ALL = 3

TRAP_STEP_PERCENT = 25

STARTER_UNLOCK_CHOICES = [
    "Unlock Grassland 1",
    "Unlock Grassland 2",
    "Unlock Grassland 3",
    "Unlock Grassland 4",
    "Unlock Hill Country 1"
]
OPENING_STREET_EXIT = "Opening Street: Exit"
OPENING_STREET_BOOK = "Opening Street: Book"
OPENING_STREET_ENEMIES = [
    "Opening Street: Green Smiley Walker",
    "Opening Street: Cyan Smiley Walker",
    "Opening Street: Red Smiley Walker",
    "Opening Street: Blue X Walker"
]
OPENING_STREET_BOSS = "Opening Street: Grey Boss Smiley Walker"

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

GOAL_LOCATIONS = {
    "Volcano": [
        "Volcano: Exit",
        "Volcano: Book",
        "Volcano: Yellow Boss Box Eel",
    ],
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
        "Hell Castle: Hell Castle Boss"
    ]
}

GOAL_OPTIONS_MAP = {
    0: ["Hell Castle"],
    1: ["Volcano"],
    2: ["Mountaintop"],
    3: ["Hell Castle", "Volcano"],
    4: ["Hell Castle", "Mountaintop"],
    5: ["Volcano", "Mountaintop"],
    6: ["Hell Castle", "Volcano", "Mountaintop"],
}

class StickRanger(World):
    game = "Stick Ranger"
    worldversion = "0.6.1"
    options_dataclass = SROptions
    options: SROptions
    location_name_to_id = location_name_to_id
    item_name_to_id = { name: data.code for name, data in item_table.items() }
    start_inventory = {}


    def create_regions(self):
        if self.options.shuffle_books == 0 and self.options.shuffle_enemies == 0:
            raise OptionError(
                "At least one of 'shuffle_books' or 'shuffle_enemies' must be enabled."
            )

        menu_region = Region("Menu", self.player, self.multiworld)
        world_map_region = Region("World Map", self.player, self.multiworld)
        self.multiworld.regions += [menu_region, world_map_region]
        menu_to_world_map_exit = Entrance(self.player, "World Map", menu_region)
        menu_region.exits.append(menu_to_world_map_exit)
        menu_to_world_map_exit.connect(world_map_region)

        def filter_locations(table, region, filter_func=None):
            return {
                loc["name"]: loc_id
                for loc_id, loc in table.items()
                if loc["region"] == region and (filter_func(loc) if filter_func else True)
            }

        def make_unlock_rule(region_name):
            return lambda state: state.has(f"Unlock {region_name}", self.player)

        for region_name in regions:
            region = Region(region_name, self.player, self.multiworld)

            stage_locs = filter_locations(stages_table, region_name)
            region.add_locations(stage_locs, SRLocation)

            if self.options.shuffle_books == 1:
                book_locs = filter_locations(books_table, region_name)
                region.add_locations(book_locs, SRLocation)

            if self.options.shuffle_enemies > 0:
                enemy_filters = {
                    ENEMIES_NORMAL: lambda loc: "boss" not in loc["name"].lower(),
                    ENEMIES_BOSS: lambda loc: "boss" in loc["name"].lower(),
                    ENEMIES_ALL: None
                }

                enemy_locations = filter_locations(enemies_table, region_name, enemy_filters.get(self.options.shuffle_enemies))
                region.add_locations(enemy_locations, SRLocation)

            self.multiworld.regions.append(region)

            world_map_exit = Entrance(self.player, region_name, world_map_region)
            if region_name != "Opening Street":
                world_map_exit.access_rule = make_unlock_rule(region_name)
            world_map_region.exits.append(world_map_exit)
            world_map_exit.connect(region)

        self.location_count = len(self.multiworld.get_locations(self.player))
        self.set_non_goal_location_rules()

    def create_item(self, name: str) -> SRItem:
        item_data = item_table.get(name)
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self):
        # Make sure at least 1 Opening Street check is an early unlock
        starter_item_name = self.multiworld.random.choice(STARTER_UNLOCK_CHOICES)
        starter_item = self.create_item(starter_item_name)

        starter_location_names = [OPENING_STREET_EXIT]
        if self.options.shuffle_books == 1:
            starter_location_names.append(OPENING_STREET_BOOK)
        shuffle_enemies = self.options.shuffle_enemies
        if shuffle_enemies in (1, 3):
            starter_location_names.extend(OPENING_STREET_ENEMIES)
        if shuffle_enemies in (2, 3):
            starter_location_names.append(OPENING_STREET_BOSS)

        random_loc_name = self.multiworld.random.choice(starter_location_names)
        starter_loc = self.multiworld.get_location(random_loc_name, self.player)
        starter_loc.place_locked_item(starter_item)
        self.location_count -= 1

        itempool = []
        # Randomize Ranger Classes
        if self.options.ranger_class_randomizer:
            for cls in RANGER_CLASSES:
                if cls != self.options.ranger_class_selected.value:
                    itempool.append(self.create_item(f"Unlock {cls} Class"))

        # Add Unlock Stages into the pool
        itempool += [
            self.create_item(unlock.item_name)
            for unlock in stages
            if unlock.item_name != starter_item_name
            and (
                not self.options.ranger_class_randomizer
                or unlock.item_name != "Unlock Forget Tree"
            )
        ]

        # Add Traps
        traps_option = self.options.traps
        missing_locs = self.location_count - len(itempool)
        traps_percentage = 0
        if traps_option >= 1:
            traps_percentage = traps_option * TRAP_STEP_PERCENT

        trap_count = int((traps_percentage / 100) * missing_locs)
        trap_weights = [trap.weight for trap in traps]
        for _ in range(trap_count):
            trap = self.multiworld.random.choices(traps, weights=trap_weights, k=1)[0]
            itempool.append(self.create_item(trap.item_name))

        while len(itempool) < self.location_count:
            itempool.append(self.create_item(self.multiworld.random.choice(filler).item_name))

        self.multiworld.itempool += itempool

    def set_non_goal_location_rules(self):
        """
        For locations associated with goals not selected by the player,
        ensure only non-progression items can be placed.
        """
        chosen_goals = GOAL_OPTIONS_MAP[self.options.goal.value]
        allowed = set()
        for goal in chosen_goals:
            allowed.update(GOAL_LOCATIONS[goal])
        all_goal_locations = set().union(*GOAL_LOCATIONS.values())
        non_goal_locations = all_goal_locations - allowed

        for loc_name in non_goal_locations:
            loc = self.multiworld.get_location(loc_name, self.player)
            if loc:
                def only_non_progression(item):
                    """
                    Return True if the item is not a progression item (advancement).
                    Used as an item_rule to restrict placement.
                    """
                    return not item.advancement
                loc.item_rule = only_non_progression

    def fill_slot_data(self) -> dict:
        return {
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race,
            "goal": self.options.goal.value,
            "ranger_class_randomizer": self.options.ranger_class_randomizer.value,
            "ranger_class_selected": self.options.ranger_class_selected.value,
            "classes_req_for_castle": self.options.classes_req_for_castle.value,
            "classes_req_for_submarine_shrine": self.options.classes_req_for_submarine_shrine.value,
            "classes_req_for_pyramid": self.options.classes_req_for_pyramid.value,
            "classes_req_for_ice_castle": self.options.classes_req_for_ice_castle.value,
            "classes_req_for_hell_castle": self.options.classes_req_for_hell_castle.value,
            "shuffle_books": self.options.shuffle_books.value,
            "shuffle_enemies": self.options.shuffle_enemies.value,
            "gold_multiplier": self.options.gold_multiplier.value,
            "xp_multiplier": self.options.xp_multiplier.value,
            "drop_multiplier": self.options.drop_multiplier.value,
            "randomize_book_costs": self.options.randomize_book_costs.value,
            "shop_hints": self.options.shop_hints.value,
            "traps": self.options.traps.value,
            "death_link": self.options.death_link.value
        }

    set_rules = set_rules
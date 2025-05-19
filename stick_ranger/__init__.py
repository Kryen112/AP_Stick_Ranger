import random
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

    def create_item(self, name: str) -> SRItem:
        item_data = item_table.get(name)
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self):
        starter_item_name = random.choice(STARTER_UNLOCK_CHOICES)
        starter_item = self.create_item(starter_item_name)

        starter_location_names = [OPENING_STREET_EXIT]
        if self.options.shuffle_books == 1:
            starter_location_names.append(OPENING_STREET_BOOK)
        shuffle_enemies = self.options.shuffle_enemies
        if shuffle_enemies in (1, 3):
            starter_location_names.extend(OPENING_STREET_ENEMIES)
        if shuffle_enemies in (2, 3):
            starter_location_names.append(OPENING_STREET_BOSS)

        random_loc_name = random.choice(starter_location_names)
        starter_loc = self.multiworld.get_location(random_loc_name, self.player)
        starter_loc.place_locked_item(starter_item)

        self.multiworld.itempool += [
            self.create_item(unlock.item_name)
            for unlock in stages
            if unlock.item_name != starter_item_name
        ]

    def pre_fill(self):
        missing_locs = len(self.multiworld.get_unfilled_locations()) - len(self.multiworld.itempool)
        if missing_locs <= 0:
            return

        traps_option = self.options.traps
        traps_percentage = 0
        if traps_option >= 1:
            traps_percentage = traps_option * TRAP_STEP_PERCENT

        trap_count = int((traps_percentage / 100) * missing_locs)
        trap_weights = [trap.weight for trap in traps]
        for _ in range(trap_count):
            trap = random.choices(traps, weights=trap_weights, k=1)[0]
            self.multiworld.itempool.append(self.create_item(trap.item_name))

        filler_count = missing_locs - trap_count
        self.multiworld.itempool += [
            self.create_item(random.choice(filler).item_name) for _ in range(filler_count)
        ]

    def fill_slot_data(self) -> dict:
        return {
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race,
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
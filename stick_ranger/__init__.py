import random
from BaseClasses import Region, Item, Entrance
from worlds.AutoWorld import World
from .Items import SRItem, item_table, levels, filler
from .Locations import SRLocation, location_table
from .Options import SROptions
from .Regions import region_info, locations_by_region
from .Rules import set_rules

class StickRanger(World):
    game = "Stick Ranger"
    worldversion = "0.6.1"
    options_dataclass = SROptions
    options: SROptions
    location_name_to_id = location_table
    item_name_to_id = { name: data.code for name, data in item_table.items() }
    start_inventory = {}

    def create_regions(self):
        for region_name, exits in region_info["regions"]:
            region = Region(region_name, self.player, self.multiworld)
            for exit_name in exits:
                entrance = Entrance(self.player, exit_name, region)
                if exit_name != "New Game":
                    progression_item = f"Unlock {exit_name}"
                    entrance.access_rule = lambda state, p = progression_item: state.has(p, self.player)
                region.exits.append(entrance)
            self.multiworld.regions.append(region)

        for entrance_name, region_name in region_info["mandatory_connections"]:
            entrance = self.multiworld.get_entrance(entrance_name, self.player)
            region = self.multiworld.get_region(region_name, self.player)
            entrance.connect(region)

        for region_name, locations in locations_by_region.items():
            region = self.multiworld.get_region(region_name, self.player)
            for location_name in locations:
                location = SRLocation(self.player, location_name, self.location_name_to_id.get(location_name, None), region)
                region.locations.append(location)

    def create_item(self, name: str) -> SRItem:
        item_data = item_table.get(name)
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self):
        starter_choices = [
            "Unlock Grassland 1",
            "Unlock Grassland 2",
            "Unlock Grassland 3",
            "Unlock Grassland 4",
            "Unlock Hill Country 1",
        ]
        starter_item_name = random.choice(starter_choices)
        starter_item = self.create_item(starter_item_name)
        starter_loc_name = random.choice(["Opening Street", "Opening Street Book"])
        starter_loc = self.multiworld.get_location(starter_loc_name, self.player)
        starter_loc.place_locked_item(starter_item)

        for level in levels:
            if level.item_name == starter_item_name:
                continue
            self.multiworld.itempool.append(self.create_item(level.item_name))

    def pre_fill(self):
        missing_locs = len(self.multiworld.get_unfilled_locations()) - len(self.multiworld.itempool)
        if missing_locs > 0:
            self.multiworld.itempool += [self.create_filler() for _ in range(missing_locs)]

    def create_filler(self) -> Item:
        item_data = random.choice(filler)
        return self.create_item(item_data.item_name)

    def fill_slot_data(self) -> dict:
        return {
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race,
            "gold_multiplier": self.options.gold_multiplier.value,
            "xp_multiplier": self.options.xp_multiplier.value,
            "drop_multiplier": self.options.drop_multiplier.value
        }

    set_rules = set_rules
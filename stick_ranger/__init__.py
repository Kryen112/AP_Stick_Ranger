import random
from BaseClasses import Region, Item, Entrance
from worlds.AutoWorld import World
from .Items import SRItem, item_table, levels, filler
from .Locations import SRLocation, location_table, location_name_to_id
from .Options import SROptions
from .Regions import regions
from .Rules import set_rules

class StickRanger(World):
    game = "Stick Ranger"
    worldversion = "0.6.1"
    options_dataclass = SROptions
    options: SROptions
    location_name_to_id = location_name_to_id
    item_name_to_id = { name: data.code for name, data in item_table.items() }
    start_inventory = {}

    def create_regions(self):
        menu_region = Region("Menu", self.player, self.multiworld)
        world_map_region = Region("World Map", self.player, self.multiworld)
        self.multiworld.regions += [menu_region, world_map_region]
        menu_to_world_map_exit = Entrance(self.player, "World Map", menu_region)
        menu_region.exits.append(menu_to_world_map_exit)
        menu_to_world_map_exit.connect(world_map_region)

        # Create regions and locations
        for region_name in regions:
            region = Region(region_name, self.player, self.multiworld)
            region.add_locations({
                loc["name"]: loc_id
                for loc_id, loc in location_table.items()
                if loc["region"] == region_name
            }, SRLocation)
            self.multiworld.regions.append(region)

            world_map_exit = Entrance(self.player, region_name, world_map_region)
            if region_name != "Opening Street":
                world_map_exit.access_rule = lambda st, item=f"Unlock {region_name}": st.has(item, self.player)
            world_map_region.exits.append(world_map_exit)
            world_map_exit.connect(region)

        # Sum locations for items creation
        self.location_count = len(self.multiworld.get_locations(self.player))

    def create_item(self, name: str) -> SRItem:
        item_data = item_table.get(name)
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self):
        starter_choices = [
            "Unlock Grassland 1",
            "Unlock Grassland 2",
            "Unlock Grassland 3",
            "Unlock Grassland 4",
            "Unlock Hill Country 1"
        ]
        starter_item_name = random.choice(starter_choices)
        starter_item = self.create_item(starter_item_name)
        starter_loc_name = random.choice(["Opening Street Exit", "Opening Street Book"])
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
            "drop_multiplier": self.options.drop_multiplier.value,
            "randomize_book_costs": self.options.randomize_book_costs.value
        }

    set_rules = set_rules
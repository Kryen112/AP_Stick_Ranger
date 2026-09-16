from typing import TYPE_CHECKING, Any, Dict, List, Set

from BaseClasses import Entrance, Location, LocationProgressType, Region, Tutorial
from Options import OptionError
from worlds.AutoWorld import WebWorld, World

from .Constants import *
from .Items import SRItem, TrapItemData, filler, item_table, stages, traps
from .Locations import (LocationDict, SRLocation, books_table, enemies_table,
                        location_name_to_id, stages_table)
from .Options import SROptions
from .Regions import regions
from .Rules import set_rules

if TYPE_CHECKING:
    from random import Random


class StickRangerWeb(WebWorld):
    tutorials: List[Tutorial] = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up the Stick Ranger randomizer connected to an Archipelago Multiworld.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Kryen112"],
        )
    ]


class StickRanger(World):
    """
    Stick Ranger is a unique 2D action RPG developed by Dan-Ball.
    Assemble a team of rangers, customize their classes, and battle through a variety of stages filled with enemies.
    """

    game: str = "Stick Ranger"
    options_dataclass = SROptions
    options: SROptions
    location_name_to_id: Dict[str, int] = location_name_to_id
    item_name_to_id: Dict[str, int] = {
        name: data.code for name, data in item_table.items()
    }
    web: StickRangerWeb = StickRangerWeb()

    def _validate_options(self) -> None:
        """Raise if neither books nor enemies are shuffled."""
        if (
            self.options.shuffle_books.value == 0
            and self.options.shuffle_enemies.value == 0
        ):
            raise OptionError(
                "At least one of 'shuffle_books' or 'shuffle_enemies' must be enabled."
            )

    def _compute_excluded_locations(self) -> Set[str]:
        """
        Compute which goal-locations should be excluded based on the currently selected goal option.
        """
        # 1) Find which sub‐goals were chosen
        chosen_goals: List[str] = GOAL_OPTIONS_MAP[self.options.goal.value]

        # 2) Build the set of all allowed locations
        allowed: Set[str] = set()
        for goal in chosen_goals:
            allowed.update(GOAL_LOCATIONS[goal])

        # 3) Compute all goal locations and subtract the allowed ones
        all_goal_locations: Set[str] = set().union(*GOAL_LOCATIONS.values())
        non_goal_locations: Set[str] = all_goal_locations - allowed

        # 4) Only exclude those that actually exist in this world
        existing: Set[str] = set(self.location_name_to_id.keys())
        return non_goal_locations & existing

    def _resolve_class_requirements(self) -> None:
        """
        Turn the raw 'classes required' options into the values the rules use.

        Class Randomizer off means no class is ever shuffled, so every gate drops
        to 0. Otherwise the gates are clamped to be non-decreasing: asking for 5
        classes at the Castle and 2 at the Pyramid would let the Pyramid look
        easier than a boss you already passed, so the Pyramid inherits the 5.

        Writing the result back onto the options is what makes fill_slot_data
        ship the resolved numbers, so the client's stage colouring gates on the
        same values as the generator.
        """
        if not self.options.ranger_class_randomizer:
            for option_name in CLASS_REQ_OPTIONS:
                getattr(self.options, option_name).value = 0
            return

        required: int = 0
        for option_name in CLASS_REQ_OPTIONS:
            option = getattr(self.options, option_name)
            required = max(required, option.value)
            option.value = required

    def _generate_randomness(self) -> None:
        """Clamp min/max and roll actual required stages per goal."""
        rng: Random = self.multiworld.random
        for _, min_attr, max_attr, req_attr in STAGE_SETTINGS:
            low: int = min(
                getattr(self.options, min_attr).value,
                getattr(self.options, max_attr).value,
            )
            high: int = max(
                getattr(self.options, min_attr).value,
                getattr(self.options, max_attr).value,
            )
            opt_min = getattr(self.options, min_attr)
            opt_max = getattr(self.options, max_attr)
            opt_min.value = low
            opt_max.value = high
            getattr(self.options, req_attr).value = rng.randint(low, high)

    def generate_early(self) -> None:
        self._validate_options()
        self.excluded_locations: Set[str] = self._compute_excluded_locations()
        self._resolve_class_requirements()
        self._generate_randomness()

    def create_regions(self) -> None:
        menu_region: Region = Region("Menu", self.player, self.multiworld)
        world_map_region: Region = Region("World Map", self.player, self.multiworld)
        self.multiworld.regions += [menu_region, world_map_region]
        menu_to_world_map_exit: Entrance = Entrance(
            self.player, "World Map", menu_region
        )
        menu_region.exits.append(menu_to_world_map_exit)
        menu_to_world_map_exit.connect(world_map_region)

        def filter_locations(
            table: Dict[int, LocationDict], region: str, filter_func=None
        ) -> Dict[str, int]:
            return {
                loc["name"]: loc_id
                for loc_id, loc in table.items()
                if loc["region"] == region
                and (filter_func(loc) if filter_func else True)
            }

        def make_unlock_rule(region_name: str) -> bool:
            return lambda state: state.has(f"Unlock {region_name}", self.player)

        for region_name in regions:
            region: Region = Region(region_name, self.player, self.multiworld)

            stage_locs: Dict[str, int] = filter_locations(stages_table, region_name)
            region.add_locations(stage_locs, SRLocation)

            if self.options.shuffle_books.value == 1:
                book_locs: Dict[str, int] = filter_locations(books_table, region_name)
                region.add_locations(book_locs, SRLocation)

            if self.options.shuffle_enemies.value > 0:
                enemy_filters: Dict[int, Any] = {
                    ENEMIES_OPTION_NON_BOSS: lambda loc: "boss"
                    not in loc["name"].lower(),
                    ENEMIES_OPTION_BOSS: lambda loc: "boss" in loc["name"].lower(),
                    ENEMIES_OPTION_ALL: None,
                }

                enemy_locations: Dict[str, int] = filter_locations(
                    enemies_table,
                    region_name,
                    enemy_filters.get(self.options.shuffle_enemies.value),
                )
                region.add_locations(enemy_locations, SRLocation)

            self.multiworld.regions.append(region)

            world_map_exit: Entrance = Entrance(
                self.player, region_name, world_map_region
            )
            if region_name != "Opening Street":
                world_map_exit.access_rule = make_unlock_rule(region_name)
            world_map_region.exits.append(world_map_exit)
            world_map_exit.connect(region)

        self._exclude_non_goal_locations()
        self.location_count: int = len(self.multiworld.get_locations(self.player))

    def _exclude_non_goal_locations(self) -> None:
        """
        Keep progression out of boss stages this seed's goal does not use.

        Volcano, Mountaintop and Hell Castle all stay playable whatever the goal
        is, but a goal you were never asked to finish should not be the thing
        standing between you and someone else's progression item.
        """
        own_locations: Set[str] = {
            location.name for location in self.multiworld.get_locations(self.player)
        }
        for location_name in self.excluded_locations & own_locations:
            location: Location = self.multiworld.get_location(location_name, self.player)
            location.progress_type = LocationProgressType.EXCLUDED

    def create_item(self, name: str) -> SRItem:
        item_data: Any | None = item_table.get(name)
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self) -> None:
        # Make sure at least 1 Opening Street check is an early unlock
        starter_item_name: str = self.multiworld.random.choice(STARTER_UNLOCK_CHOICES)
        starter_item: SRItem = self.create_item(starter_item_name)

        starter_location_names: List[str] = [OPENING_STREET_EXIT]
        if self.options.shuffle_books.value == 1:
            starter_location_names.append(OPENING_STREET_BOOK)
        shuffle_enemies: int = self.options.shuffle_enemies.value
        if shuffle_enemies in (1, 3):
            starter_location_names.extend(OPENING_STREET_ENEMIES)
        if shuffle_enemies in (2, 3):
            starter_location_names.append(OPENING_STREET_BOSS)

        random_loc_name: str = self.multiworld.random.choice(starter_location_names)
        starter_loc: Location = self.multiworld.get_location(
            random_loc_name, self.player
        )
        starter_loc.place_locked_item(starter_item)
        self.location_count -= 1

        itempool: List[SRItem] = []
        # Add Ranger Classes
        if self.options.ranger_class_randomizer.value:
            for cls in RANGER_CLASSES:
                if cls != self.options.ranger_class_selected.value:
                    itempool.append(self.create_item(f"Unlock {cls} Class"))

        # Add Unlock Stages into the pool
        itempool.extend(
            self.create_item(unlock.item_name)
            for unlock in stages
            if unlock.item_name != starter_item_name
            and (
                not self.options.ranger_class_randomizer.value
                or unlock.item_name != "Unlock Forget Tree"
            )
        )

        # Add Traps
        traps_option: int = self.options.traps.value
        missing_locs: int = self.location_count - len(itempool)
        traps_percentage: int = 0
        if traps_option >= 1:
            traps_percentage = traps_option * TRAP_STEP_PERCENT

        trap_count: int = int((traps_percentage / 100) * missing_locs)
        trap_weights: List[int] = [trap.weight for trap in traps]
        for _ in range(trap_count):
            trap: TrapItemData = self.multiworld.random.choices(
                traps, weights=trap_weights, k=1
            )[0]
            itempool.append(self.create_item(trap.item_name))

        # Add Filler
        while len(itempool) < self.location_count:
            itempool.append(
                self.create_item(self.multiworld.random.choice(filler).item_name)
            )

        self.multiworld.itempool += itempool

    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data: Dict[str, Any] = self.options.as_dict(
            "goal",
            "ranger_class_randomizer",
            "ranger_class_selected",
            "classes_req_for_castle",
            "classes_req_for_submarine_shrine",
            "classes_req_for_pyramid",
            "classes_req_for_ice_castle",
            "classes_req_for_hell_castle",
            "stages_req_for_castle",
            "stages_req_for_submarine_shrine",
            "stages_req_for_pyramid",
            "stages_req_for_ice_castle",
            "stages_req_for_hell_castle",
            "shuffle_books",
            "shuffle_enemies",
            "gold_multiplier",
            "xp_multiplier",
            "drop_multiplier",
            "randomize_book_costs",
            "shop_hints",
            "traps",
            "remove_null_compo",
            "death_link",
        )
        slot_data.update(
            {
                "player_name": self.multiworld.get_player_name(self.player),
                "player_id": self.player,
            }
        )
        return slot_data

    set_rules = set_rules

from __future__ import annotations

from typing import Any, Callable

from BaseClasses import CollectionState, Location, LocationProgressType, Region, Tutorial
from Options import OptionError
from worlds.AutoWorld import WebWorld, World

from .constants import (
    CLASS_REQ_OPTIONS,
    ENEMIES_OPTION_ALL,
    ENEMIES_OPTION_BOSS,
    ENEMIES_OPTION_NON_BOSS,
    GOAL_LOCATIONS,
    GOAL_OPTIONS_MAP,
    OPENING_STREET_BOOK,
    OPENING_STREET_BOSS,
    OPENING_STREET_ENEMIES,
    OPENING_STREET_EXIT,
    RANGER_CLASSES,
    ROLLED_OPTIONS,
    STAGE_SETTINGS,
    STARTER_UNLOCK_CHOICES,
    TRAP_SHARE_BY_OPTION,
)
from .items import (
    PROGRESSIVE_SHOP,
    PROGRESSIVE_SHOP_TIERS,
    SRItem,
    filler,
    item_name_groups,
    item_table,
    stages,
    traps,
)
from .locations import (
    LocationDict,
    SRLocation,
    books_table,
    enemies_table,
    location_name_groups,
    location_name_to_id,
    stages_table,
)
from .options import SR_OPTION_GROUPS, SROptions
from .regions import regions
from .rules import set_region_rules

WORLD_MAP = "World Map"


class StickRangerWeb(WebWorld):
    theme = "grass"
    bug_report_page = "https://github.com/Kryen112/AP_Stick_Ranger/issues"
    option_groups = SR_OPTION_GROUPS
    tutorials = [
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

    game = "Stick Ranger"
    options_dataclass = SROptions
    options: SROptions
    web = StickRangerWeb()

    location_name_to_id = location_name_to_id
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    item_name_groups = item_name_groups
    location_name_groups = location_name_groups

    excluded_locations: set[str]
    location_count: int

    # ------------------------------------------------------------------ setup

    def generate_early(self) -> None:
        self._validate_options()
        self.excluded_locations = self._compute_excluded_locations()
        restored = self._tracker_passthrough()
        if restored is None:
            self._resolve_class_requirements()
            self._roll_stage_requirements()
        else:
            self._restore_requirements(restored)

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        """
        Universal Tracker hook.

        The boss gates are decided during generation, so a tracker rebuilding
        the world from the yaml alone rolls its own numbers and then disagrees
        with the seed about what is in logic. Returning slot_data asks UT to
        re-generate with it, and generate_early reads it back below.
        """
        return slot_data

    def _tracker_passthrough(self) -> "dict[str, Any] | None":
        """The slot_data Universal Tracker handed back, if this is a UT re-gen."""
        passthrough = getattr(self.multiworld, "re_gen_passthrough", None)
        if not passthrough:
            return None
        return passthrough.get(self.game)

    def _restore_requirements(self, slot_data: dict[str, Any]) -> None:
        """Use the seed's own rolled values rather than rolling new ones."""
        for option_name in ROLLED_OPTIONS:
            if option_name in slot_data:
                getattr(self.options, option_name).value = slot_data[option_name]

    def _validate_options(self) -> None:
        """Raise if neither books nor enemies are shuffled."""
        if not self.options.shuffle_books and not self.options.shuffle_enemies:
            raise OptionError(
                "At least one of 'shuffle_books' or 'shuffle_enemies' must be enabled."
            )

    def _compute_excluded_locations(self) -> set[str]:
        """
        Locations belonging to a boss stage this seed's goal does not use.

        Every boss stage stays playable whatever the goal is -- this only keeps
        progression out of the ones you were never asked to finish.
        """
        allowed: set[str] = set()
        for goal in GOAL_OPTIONS_MAP[self.options.goal.value]:
            allowed.update(GOAL_LOCATIONS[goal])
        every_goal_location: set[str] = set().union(*GOAL_LOCATIONS.values())
        return every_goal_location - allowed

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

        required = 0
        for option_name in CLASS_REQ_OPTIONS:
            option = getattr(self.options, option_name)
            required = max(required, option.value)
            option.value = required

    def _roll_stage_requirements(self) -> None:
        """Order each boss gate's min/max, then roll the count this seed uses."""
        for _, min_attr, max_attr, required_attr in STAGE_SETTINGS:
            minimum = getattr(self.options, min_attr)
            maximum = getattr(self.options, max_attr)
            minimum.value, maximum.value = (
                min(minimum.value, maximum.value),
                max(minimum.value, maximum.value),
            )
            getattr(self.options, required_attr).value = self.random.randint(
                minimum.value, maximum.value
            )

    # ---------------------------------------------------------------- regions

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        world_map = Region(WORLD_MAP, self.player, self.multiworld)
        self.multiworld.regions += [menu, world_map]
        menu.connect(world_map, WORLD_MAP)

        for region_name in regions:
            region = Region(region_name, self.player, self.multiworld)
            region.add_locations(self._locations_in(region_name), SRLocation)
            self.multiworld.regions.append(region)
            # rules.py replaces most of these; Opening Street is free, and the
            # pre-Castle stages never need more than their own unlock.
            world_map.connect(
                region,
                region_name,
                None if region_name == "Opening Street" else self._unlock_rule(region_name),
            )

        self._exclude_non_goal_locations()
        self.location_count = len(self.multiworld.get_locations(self.player))

    def _locations_in(self, region_name: str) -> dict[str, int]:
        """Every location this seed's options put in one stage."""
        found = self._filter(stages_table, region_name)
        if self.options.shuffle_books:
            found.update(self._filter(books_table, region_name))
        if self.options.shuffle_enemies:
            enemy_filters: dict[int, Callable[[LocationDict], bool] | None] = {
                ENEMIES_OPTION_NON_BOSS: lambda loc: "boss" not in loc["name"].lower(),
                ENEMIES_OPTION_BOSS: lambda loc: "boss" in loc["name"].lower(),
                ENEMIES_OPTION_ALL: None,
            }
            found.update(
                self._filter(
                    enemies_table,
                    region_name,
                    enemy_filters[self.options.shuffle_enemies.value],
                )
            )
        return found

    @staticmethod
    def _filter(
        table: dict[int, LocationDict],
        region_name: str,
        keep: Callable[[LocationDict], bool] | None = None,
    ) -> dict[str, int]:
        return {
            location["name"]: location_id
            for location_id, location in table.items()
            if location["region"] == region_name and (keep is None or keep(location))
        }

    def _unlock_rule(self, region_name: str) -> Callable[[CollectionState], bool]:
        return lambda state: state.has(f"Unlock {region_name}", self.player)

    def _exclude_non_goal_locations(self) -> None:
        """Keep progression out of boss stages this seed's goal does not use."""
        for location in self.multiworld.get_locations(self.player):
            if location.name in self.excluded_locations:
                location.progress_type = LocationProgressType.EXCLUDED

    def set_rules(self) -> None:
        goal_exits = GOAL_OPTIONS_MAP[self.options.goal.value]
        self.multiworld.completion_condition[self.player] = lambda state: all(
            state.can_reach_location(f"{goal}: Exit", self.player) for goal in goal_exits
        )
        set_region_rules(self.player, self.multiworld, self.options)

    # ------------------------------------------------------------------ items

    def create_item(self, name: str) -> SRItem:
        item_data = item_table[name]
        return SRItem(name, item_data.classification, item_data.code, self.player)

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler).item_name

    def create_items(self) -> None:
        self._place_starter_unlock()

        itempool: list[SRItem] = []

        if self.options.ranger_class_randomizer:
            itempool.extend(
                self.create_item(f"Unlock {ranger_class} Class")
                for ranger_class in RANGER_CLASSES
                if ranger_class != self.options.ranger_class_selected.value
            )

        itempool.extend(
            self.create_item(unlock.item_name)
            for unlock in stages
            if unlock.item_name != self.starter_item_name
            # Class Randomizer starts you at the Forget Tree so you can swap
            # classes, so its unlock would be a dud item.
            and not (
                self.options.ranger_class_randomizer
                and unlock.item_name == "Unlock Forget Tree"
            )
        )

        if self.options.progressive_shop:
            itempool.extend(
                self.create_item(PROGRESSIVE_SHOP) for _ in range(PROGRESSIVE_SHOP_TIERS)
            )

        itempool.extend(self._create_traps(self.location_count - len(itempool)))
        while len(itempool) < self.location_count:
            itempool.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool += itempool

    def _place_starter_unlock(self) -> None:
        """
        Lock an early stage unlock onto an Opening Street check.

        Opening Street is the only stage you can play with nothing, so without
        this a seed can open with no reachable progression at all.
        """
        self.starter_item_name: str = self.random.choice(STARTER_UNLOCK_CHOICES)

        candidates = [OPENING_STREET_EXIT]
        if self.options.shuffle_books:
            candidates.append(OPENING_STREET_BOOK)
        if self.options.shuffle_enemies.value in (ENEMIES_OPTION_NON_BOSS, ENEMIES_OPTION_ALL):
            candidates.extend(OPENING_STREET_ENEMIES)
        if self.options.shuffle_enemies.value in (ENEMIES_OPTION_BOSS, ENEMIES_OPTION_ALL):
            candidates.append(OPENING_STREET_BOSS)

        location: Location = self.get_location(self.random.choice(candidates))
        location.place_locked_item(self.create_item(self.starter_item_name))
        self.location_count -= 1

    def _create_traps(self, open_locations: int) -> list[SRItem]:
        if not self.options.traps:
            return []
        share = TRAP_SHARE_BY_OPTION[self.options.traps.value] / 100
        weights = [trap.weight for trap in traps]
        return [
            self.create_item(self.random.choices(traps, weights=weights, k=1)[0].item_name)
            for _ in range(int(share * open_locations))
        ]

    # -------------------------------------------------------------- slot data

    def fill_slot_data(self) -> dict[str, Any]:
        slot_data = self.options.as_dict(
            "goal",
            "ranger_class_randomizer",
            "ranger_class_selected",
            *CLASS_REQ_OPTIONS,
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
            "free_respec",
            "progressive_shop",
            "remove_null_compo",
            "death_link",
        )
        slot_data["player_name"] = self.player_name
        slot_data["player_id"] = self.player
        return slot_data

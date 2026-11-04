from __future__ import annotations

from typing import Any, Callable

from BaseClasses import (
    CollectionState,
    ItemClassification,
    Location,
    LocationProgressType,
    MultiWorld,
    Region,
    Tutorial,
)
from Options import OptionError
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, Type, components

from .constants import (
    CLASS_REQ_OPTIONS,
    ENEMIES_OPTION_ALL,
    ENEMIES_OPTION_BOSS,
    ENEMIES_OPTION_NON_BOSS,
    GOAL_OPTIONS_MAP,
    OPENING_STREET_BOOK,
    OPENING_STREET_BOSS,
    OPENING_STREET_ENEMIES,
    OPENING_STREET_EXIT,
    RANGER_CLASSES,
    SLOT_DATA_OPTIONS,
    STAGE_SETTINGS,
    STARTER_UNLOCK_CHOICES,
)
from .items import (
    FILLER_TIER,
    PROGRESSIVE_SHOPS,
    SHOP_PROGRESSION_FIRST,
    SHOP_PROGRESSION_STEPS,
    SHOP_TOWN_UNLOCKS,
    SRItem,
    item_name_groups,
    item_table,
    stage_id,
    stages,
    traps,
)
from .base import LocationDict, SRLocation
from .goal import TOWN_AREAS, GoalScope, filler_within, loot_tier_cap
from .locations import (
    books_table,
    enemies_table,
    location_name_groups,
    location_name_to_id,
    stages_table,
)
from .options import SR_OPTION_GROUPS, SROptions
from .shop import shop_table
from .regions import TOWN_REGIONS, regions
from .client import launch_client
from .rules import CHAIN_BOSSES, logic_description, set_region_rules, set_shop_rules

components.append(
    Component(
        "Stick Ranger Client",
        func=launch_client,
        component_type=Type.CLIENT,
        game_name="Stick Ranger",
        supports_uri=True,
        description="Open Stick Ranger on dan-ball.jp, where the Stick Ranger Archipelago userscript "
        "connects it; from a room page, the connect form is filled in for you.",
    )
)

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

    location_count: int
    scope: GoalScope
    filler_names: list[str]
    gates: dict[str, Callable[[CollectionState], bool]]

    # Universal Tracker can rebuild the world from slot_data alone, with no
    # yaml: every option ships, and generate_early reads them all back.
    ut_can_gen_without_yaml = True

    # ------------------------------------------------------------------ setup

    def generate_early(self) -> None:
        restored = self._tracker_passthrough()
        if restored is not None:
            self._restore_options(restored)
        self._migrate_legacy_options()
        self._validate_options()
        self._resolve_shop_options()
        self._resolve_ring_options()
        self.scope = GoalScope(self.options.goal.value)
        self.filler_names = filler_within(
            self.scope.loot_tier_cap if self.options.cap_loot_at_goal else max(FILLER_TIER.values())
        )
        if restored is None:
            self._resolve_class_requirements()
            self._roll_stage_requirements()

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        """
        Universal Tracker hook.

        The boss gates are decided during generation, so a tracker rebuilding
        the world from the yaml alone rolls its own numbers and then disagrees
        with the seed about what is in logic. Returning slot_data asks UT to
        re-generate with it, and generate_early reads every option back from
        it -- the rolled gates and the ones a player set alike, which is what
        lets UT skip the yaml altogether.
        """
        return slot_data

    def _tracker_passthrough(self) -> "dict[str, Any] | None":
        """The slot_data Universal Tracker handed back, if this is a UT re-gen."""
        passthrough = getattr(self.multiworld, "re_gen_passthrough", None)
        if not passthrough:
            return None
        return passthrough.get(self.game)

    def _restore_options(self, slot_data: dict[str, Any]) -> None:
        """
        Use the seed's own option values rather than the yaml's, or defaults.

        The rolled and clamped values come back resolved, so nothing is rolled
        over the top of them; every other option comes back too, so a tracker
        started without a yaml still builds the same world.
        """
        for option_name in SLOT_DATA_OPTIONS:
            if option_name in slot_data:
                value = slot_data[option_name]
                # JSON has no sets, so an OptionSet comes back as a list.
                if isinstance(value, list):
                    value = set(value)
                getattr(self.options, option_name).value = value

    def _migrate_legacy_options(self) -> None:
        """
        Fold the 1.8 yaml keys into the options that replaced them.

        `traps` became Trap Percentage and `important_hints_only` became a value
        of Shop Hints. Archipelago only warns about a key it does not know, so a
        yaml still using the old ones would otherwise generate with no traps and
        every shop item hinted, and nobody would see why. The old key only
        counts while the new one is still at its default.
        """
        if self.options.traps.value and not self.options.trap_percentage.value:
            self.options.trap_percentage.value = self.options.traps.value
        shop_hints = self.options.shop_hints
        if self.options.important_hints_only and shop_hints.value == shop_hints.option_all:
            shop_hints.value = shop_hints.option_important_only

    def _validate_options(self) -> None:
        """Raise unless something in the seed actually produces checks."""
        if not (
            self.options.shuffle_books
            or self.options.shuffle_enemies
            or self.options.shop_checks
        ):
            raise OptionError(
                "At least one of 'shuffle_books', 'shuffle_enemies' or "
                "'shop_checks' must be enabled."
            )

    def _resolve_shop_options(self) -> None:
        """
        Progressive Shop and Enforce Shop Logic only mean something once the
        shop holds checks. Zeroing them here is what makes fill_slot_data ship
        0, so the client neither gates nor greys a shop logic never looked at.
        """
        if not self.options.shop_checks:
            self.options.progressive_shop.value = 0
            self.options.enforce_shop_logic.value = 0

    def _resolve_ring_options(self) -> None:
        """
        Gold per Thrown Ring is Ring Link's payout: the rings your Angels throw
        are what you send the room. Without Ring Link it would be a plain gold
        faucet, so it is zeroed and the client is told 0.
        """
        if not self.options.ring_link:
            self.options.ring_gold.value = 0

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

        towns = [town for town in TOWN_REGIONS if self._town_in_play(town)]
        for region_name in [*regions, *(towns if self.options.shop_checks else [])]:
            region = Region(region_name, self.player, self.multiworld)
            # A stage past the goal keeps its region, so the gates and Town's
            # stocking rule can still name it, but holds nothing to check.
            if not self.scope.is_cut(region_name):
                region.add_locations(self._locations_in(region_name), SRLocation)
            self.multiworld.regions.append(region)
            # rules.py replaces most of these; Opening Street is free, and the
            # pre-Castle stages never need more than their own unlock.
            world_map.connect(
                region,
                region_name,
                None
                if region_name in ("Opening Street", "Town")
                else self._unlock_rule(region_name),
            )

        self._exclude_side_boss_locations()
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
        if self.options.shop_checks:
            found.update(
                self._filter(
                    shop_table,
                    region_name,
                    lambda loc: not self.scope.is_shop_check_cut(loc),
                )
            )
        return found

    def _town_in_play(self, town: str) -> bool:
        """Town always is; the others only when the yaml keeps them and the goal reaches them."""
        if town not in TOWN_AREAS:
            return True
        return town in self.options.towns_in_pool.value and not self.scope.is_cut(town)

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

    def _exclude_side_boss_locations(self) -> None:
        """
        Keep progression out of boss stages this seed's goal does not use.

        They stay playable, so a Hell Castle goal can still take on Volcano for
        fun, but nothing anyone needs is ever waiting there.
        """
        for location in self.multiworld.get_locations(self.player):
            if self.scope.is_side_boss(location.parent_region.name):
                location.progress_type = LocationProgressType.EXCLUDED

    def set_rules(self) -> None:
        goal_exits = GOAL_OPTIONS_MAP[self.options.goal.value]
        self.multiworld.completion_condition[self.player] = lambda state: all(
            state.can_reach_location(f"{goal}: Exit", self.player) for goal in goal_exits
        )
        self.gates = set_region_rules(self.player, self.multiworld, self.options)
        if self.options.shop_checks:
            set_shop_rules(self.player, self.multiworld, self.options, self.gates)

    # ------------------------------------------------------------------ items

    def create_item(self, name: str) -> SRItem:
        item_data = item_table[name]
        return SRItem(name, self._classify(name, item_data.classification), item_data.code, self.player)

    def _classify(self, name: str, default: ItemClassification) -> ItemClassification:
        """
        Shop checks turn two kinds of useful item into progression.

        Nothing is gated behind a Progressive Shop item or a town unlock until
        the shop holds checks; once it does, both stand between the player and a
        location, and fill has to know that or it can strand them.
        """
        if not self.options.shop_checks:
            return default
        if name in PROGRESSIVE_SHOPS.values() or name in SHOP_TOWN_UNLOCKS.values():
            return ItemClassification.progression
        return default

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.filler_names)

    def create_items(self) -> None:
        self._place_starter_unlock()

        itempool: list[SRItem] = []

        if self.options.ranger_class_randomizer:
            itempool.extend(self.create_item(name) for name in self._class_unlocks())

        itempool.extend(
            self.create_item(unlock.item_name)
            for unlock in stages
            if unlock.item_name != self.starter_item_name
            and self._unlock_in_pool(unlock.item_name.removeprefix("Unlock "))
            # Class Randomizer starts you at the Forget Tree so you can swap
            # classes, so its unlock would be a dud item.
            and not (
                self.options.ranger_class_randomizer
                and unlock.item_name == "Unlock Forget Tree"
            )
        )

        if self.options.progressive_shop:
            itempool.extend(self.create_item(name) for name in self._progressive_shop_items())

        if len(itempool) > self.location_count:
            raise OptionError(
                f"Stick Ranger: {self.player_name}'s options leave {self.location_count} "
                f"checks for {len(itempool)} unlocks. Turn on more of Shuffle Books, "
                f"Shuffle Enemies or Shop Checks, or pick a later goal."
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

    def _unlock_in_pool(self, stage: str) -> bool:
        if stage in TOWN_AREAS:
            return self._town_in_play(stage)
        return not self.scope.is_cut(stage)

    def _class_unlocks(self) -> list[str]:
        """
        The class unlocks to shuffle, starting class left out.

        Surplus Classes decides what happens to the ones the goal does not
        need: shuffled anyway, dropped, or handed over at the start. Which ones
        are surplus is rolled only when that matters, so a seed with the option
        at its default rolls exactly what it did before the option existed.
        """
        unlocks = [
            f"Unlock {ranger_class} Class"
            for ranger_class in RANGER_CLASSES
            if ranger_class != self.options.ranger_class_selected.value
        ]
        surplus_classes = self.options.surplus_classes
        if surplus_classes == surplus_classes.option_in_pool:
            return unlocks

        # The starting class counts towards every requirement.
        required = max(getattr(self.options, name).value for name in self.scope.class_options)
        needed = sorted(self.random.sample(unlocks, min(len(unlocks), max(0, required - 1))))
        if surplus_classes == surplus_classes.option_start_with:
            for name in unlocks:
                if name not in needed:
                    self.multiworld.push_precollected(self.create_item(name))
        return needed

    def _progressive_shop_items(self) -> list[str]:
        """
        One track per shop, as long as the deepest row still in the seed.

        Only reached with Shop Checks on, which brings 462 locations of its own,
        so the 81 items always fit: they used to be trimmed to a small seed and
        leave the deepest rows unopenable. A goal that cuts rows cuts the items
        that would only have opened them, and a town out of play has no track.
        """
        present = {location.name for location in self.multiworld.get_locations(self.player)}
        deepest: dict[str, int] = {}
        for entry in shop_table.values():
            if entry["name"] in present:
                deepest[entry["region"]] = max(deepest.get(entry["region"], 0), entry["req"])
        return [
            name
            for town, name in PROGRESSIVE_SHOPS.items()
            for _ in range(deepest.get(town, 0))
        ]

    def _create_traps(self, open_locations: int) -> list[SRItem]:
        if not self.options.trap_percentage:
            return []
        share = self.options.trap_percentage.value / 100
        weights = [trap.weight for trap in traps]
        return [
            self.create_item(self.random.choices(traps, weights=weights, k=1)[0].item_name)
            for _ in range(int(share * open_locations))
        ]

    # ------------------------------------------------------------------- loot

    @classmethod
    def stage_post_fill(cls, multiworld: MultiWorld) -> None:
        """
        Scale Loot with Progress: re-roll filler that Archipelago expects to be
        found before its owner could reach the area that tier drops in.

        Walks the spheres the way the playthrough does. Each filler item is
        judged by its owner's gates as they stand when its sphere opens, wherever
        in the multiworld it was placed, and swapped for one of a tier that fits.
        Swapping filler for filler never touches logic, so the fill stays valid.
        """
        worlds: dict[int, StickRanger] = {
            world.player: world
            for world in multiworld.get_game_worlds(cls.game)
            if world.options.scale_loot_with_progress
        }
        if not worlds:
            return

        state = CollectionState(multiworld)
        locations = set(multiworld.get_filled_locations())
        while locations:
            sphere = {location for location in locations if location.can_reach(state)}
            if not sphere:
                break
            caps = {player: world._loot_cap(state) for player, world in worlds.items()}
            for location in sphere:
                item = location.item
                if (
                    item.player in caps
                    and item.name in FILLER_TIER
                    and FILLER_TIER[item.name] > caps[item.player]
                ):
                    world = worlds[item.player]
                    replacement = world.create_item(
                        world.random.choice(filler_within(caps[item.player]))
                    )
                    replacement.location = location
                    location.item = replacement
            for location in sphere:
                state.collect(location.item, True, location)
            locations -= sphere

    def _loot_cap(self, state: CollectionState) -> int:
        """The highest filler tier this player has reached the area of."""
        gates_open = 0
        for boss_stage in CHAIN_BOSSES:
            if not self.gates[boss_stage](state):
                break
            gates_open += 1
        cap = loot_tier_cap(gates_open)
        if self.options.cap_loot_at_goal:
            cap = min(cap, self.scope.loot_tier_cap)
        return cap

    # -------------------------------------------------------------- slot data

    def fill_slot_data(self) -> dict[str, Any]:
        slot_data = self.options.as_dict(*SLOT_DATA_OPTIONS)
        # The client evaluates this instead of carrying its own copy of the
        # rules, so the two cannot drift apart.
        slot_data["logic"] = logic_description(self.options, self.scope.level)
        # The stages whose clearing wins, as game stage ids. The client used to
        # keep its own copy of the goal table and had to learn every new goal.
        slot_data["goal_stages"] = [stage_id(name) for name in self.scope.goals]
        # What opens for free play once the goal is cleared: every stage and
        # town the seed never hands out an unlock for. Stages before the goal
        # that are still to arrive stay shut -- someone may yet send them.
        slot_data["free_play_stages"] = sorted(
            stage_id(name)
            for name in [*regions, *TOWN_AREAS]
            if name != "Opening Street" and not self._unlock_in_pool(name)
        )
        # How each shop opens, indexed by the game's town order. The client used
        # to carry these numbers itself; shipping them keeps the stock the
        # player sees and the rules the fill used from drifting apart.
        slot_data["shop_progression"] = {
            "ids": [item_table[name].code for name in PROGRESSIVE_SHOPS.values()],
            "steps": [SHOP_PROGRESSION_STEPS[town] for town in PROGRESSIVE_SHOPS],
            "first": [SHOP_PROGRESSION_FIRST[town] for town in PROGRESSIVE_SHOPS],
        }
        slot_data["player_name"] = self.player_name
        slot_data["player_id"] = self.player
        # Which apworld generated the seed. The client used to guess from
        # which keys were missing; now it can say so, and warn when it is
        # older or newer than the seed expects.
        slot_data["world_version"] = self.world_version.as_simple_string()
        return slot_data

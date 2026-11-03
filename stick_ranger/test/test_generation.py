"""Generation sweeps: every goal and every check-source combination has to fill
and stay beatable."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from BaseClasses import CollectionState
from Fill import distribute_items_restrictive
from Options import OptionError, PerGameCommonOptions, Visibility

from ..constants import GOAL_OPTIONS_MAP, LEGACY_OPTIONS, SLOT_DATA_OPTIONS
from ..items import (
    PROGRESSIVE_SHOP_COUNTS,
    PROGRESSIVE_SHOPS,
    SHOP_PROGRESSION_STEPS,
    SHOP_TOWN_UNLOCKS,
    filler,
    traps,
    unlocks_by_region,
)
from ..items import stage_id
from ..regions import regions
from ..rules import SHOP_TIER_GATES, region_stage_id
from ..options import SR_OPTION_GROUPS, ShopHints, SROptions, TrapPercentage
from ..shop import SHOP_REQS, shop_table
from . import StickRangerTestBase

shop_by_name = {entry["name"]: entry for entry in shop_table.values()}


class SweepTestBase(StickRangerTestBase):
    run_default_tests = False

    def pool_counts(self) -> Counter[str]:
        """Item names in the pool, which is not the same as what is collected."""
        return Counter(item.name for item in self.multiworld.itempool)

    def assertSeedWorks(self) -> None:
        """Every location fills, and the goal is reachable with the whole pool."""
        self.assertEqual(
            len(self.multiworld.itempool) + 1,   # + the starter unlock, placed locked
            len(self.multiworld.get_locations(self.player)),
            "the item pool does not fill the locations",
        )
        state = self.multiworld.get_all_state(False)
        self.assertTrue(
            self.multiworld.completion_condition[self.player](state),
            "the goal is unreachable with every item collected",
        )


class TestGoalSweep(SweepTestBase):
    def test_every_goal_generates_and_is_beatable(self) -> None:
        for goal in GOAL_OPTIONS_MAP:
            with self.subTest(goal=goal):
                self.options = {"goal": goal, "shuffle_books": 1, "shuffle_enemies": 3}
                self.world_setup()
                self.assertSeedWorks()

    def test_goal_exits_are_required(self) -> None:
        for goal, goal_stages in GOAL_OPTIONS_MAP.items():
            for stage in goal_stages:
                with self.subTest(goal=goal, stage=stage):
                    self.options = {"goal": goal, "shuffle_books": 1, "shuffle_enemies": 0}
                    self.world_setup()
                    self.collect_all_but(f"Unlock {stage}")
                    self.assertFalse(
                        self.multiworld.completion_condition[self.player](
                            self.multiworld.state
                        ),
                        f"goal {goal} completes without Unlock {stage}",
                    )


class TestCheckSourceSweep(SweepTestBase):
    def test_every_check_source_combination_fills(self) -> None:
        combinations = [
            {"shuffle_books": 1, "shuffle_enemies": 0},
            {"shuffle_books": 0, "shuffle_enemies": 1},
            {"shuffle_books": 0, "shuffle_enemies": 2},
            {"shuffle_books": 0, "shuffle_enemies": 3},
            {"shuffle_books": 1, "shuffle_enemies": 3},
        ]
        for combination in combinations:
            with self.subTest(**combination):
                self.options = combination
                self.world_setup()
                self.assertSeedWorks()

    def test_no_check_source_is_rejected(self) -> None:
        self.options = {"shuffle_books": 0, "shuffle_enemies": 0}
        with self.assertRaises(OptionError):
            self.world_setup()


class TestTrapSweep(SweepTestBase):
    def test_every_trap_level_fills(self) -> None:
        for percent in (0, 5, 10, 20, 50, 100):
            with self.subTest(trap_percentage=percent):
                self.options = {"trap_percentage": percent, "shuffle_books": 1, "shuffle_enemies": 3}
                self.world_setup()
                self.assertSeedWorks()
                trap_count = sum(1 for item in self.multiworld.itempool if item.trap)
                if percent == 0:
                    self.assertEqual(trap_count, 0)
                else:
                    self.assertGreater(trap_count, 0)

    def test_at_a_hundred_no_weapon_or_compo_is_left(self) -> None:
        """Town unlocks stay in the pool as useful items; the filler is all traps."""
        self.options = {"trap_percentage": 100, "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        filler_names = {item.item_name for item in filler}
        self.assertEqual([item.name for item in self.multiworld.itempool if item.name in filler_names], [])

    def test_old_yaml_values_still_parse(self) -> None:
        """1.8 yamls said `none` or a quoted number; both have to keep working."""
        self.assertEqual(TrapPercentage.from_any("none").value, 0)
        self.assertEqual(TrapPercentage.from_any("20").value, 20)
        self.assertEqual(TrapPercentage.from_any(5).value, 5)


class TestLegacyYamlKeys(SweepTestBase):
    """
    A 1.8 yaml still says `traps:` and `important_hints_only:`. Archipelago only
    warns about a key it does not know, so without these the yaml would generate
    with no traps and every shop item hinted, and nobody would see why.
    """

    def test_traps_is_read_as_a_percentage(self) -> None:
        self.options = {"shuffle_books": 1, "traps": 20}
        self.world_setup()
        self.assertEqual(self.world.options.trap_percentage.value, 20)
        self.assertEqual(self.world.fill_slot_data()["trap_percentage"], 20)

    def test_traps_none_still_means_none(self) -> None:
        self.options = {"shuffle_books": 1, "traps": "none"}
        self.world_setup()
        self.assertEqual(self.world.options.trap_percentage.value, 0)

    def test_the_new_key_wins_when_both_are_set(self) -> None:
        self.options = {"shuffle_books": 1, "traps": 20, "trap_percentage": 50}
        self.world_setup()
        self.assertEqual(self.world.options.trap_percentage.value, 50)

    def test_important_hints_only_folds_into_shop_hints(self) -> None:
        self.options = {"shuffle_books": 1, "shop_hints": "true", "important_hints_only": "true"}
        self.world_setup()
        self.assertEqual(self.world.options.shop_hints.value, ShopHints.option_important_only)

    def test_important_hints_only_does_not_turn_hints_back_on(self) -> None:
        self.options = {"shuffle_books": 1, "shop_hints": "false", "important_hints_only": "true"}
        self.world_setup()
        self.assertEqual(self.world.options.shop_hints.value, ShopHints.option_off)

    def test_the_old_keys_never_reach_the_client(self) -> None:
        self.options = {"shuffle_books": 1, "traps": 20, "important_hints_only": "true"}
        self.world_setup()
        slot_data = self.world.fill_slot_data()
        for name in LEGACY_OPTIONS:
            self.assertNotIn(name, slot_data, f"{name} is a yaml key, not a client option")


class TestClassRandomizerSweep(SweepTestBase):
    def test_maximum_class_requirements_still_fill(self) -> None:
        self.options = {
            "ranger_class_randomizer": 1,
            "classes_req_for_castle": 8,
            "classes_req_for_submarine_shrine": 8,
            "classes_req_for_pyramid": 8,
            "classes_req_for_ice_castle": 8,
            "classes_req_for_hell_castle": 8,
            "shuffle_books": 1,
            "shuffle_enemies": 3,
        }
        self.world_setup()
        self.assertSeedWorks()

    def test_forget_tree_unlock_is_dropped_when_class_randomizer_is_on(self) -> None:
        """The client hands you the Forget Tree, so its unlock would be a dud."""
        self.options = {"ranger_class_randomizer": 1}
        self.world_setup()
        self.assertEqual(self.pool_counts()["Unlock Forget Tree"], 0)

    def test_forget_tree_unlock_exists_otherwise(self) -> None:
        self.options = {"ranger_class_randomizer": 0}
        self.world_setup()
        self.assertEqual(self.pool_counts()["Unlock Forget Tree"], 1)

    def test_starting_class_is_not_in_the_pool(self) -> None:
        self.options = {"ranger_class_randomizer": 1, "ranger_class_selected": "boxer"}
        self.world_setup()
        counts = self.pool_counts()
        self.assertEqual(counts["Unlock Boxer Class"], 0)
        self.assertEqual(sum(1 for name in counts if name.endswith(" Class")), 7)

    def test_no_class_items_without_the_randomizer(self) -> None:
        self.options = {"ranger_class_randomizer": 0}
        self.world_setup()
        self.assertEqual(
            [name for name in self.pool_counts() if name.endswith(" Class")], []
        )


class TestMaximumStageRequirements(SweepTestBase):
    """The top of every 'stages required' range has to still be satisfiable."""

    def test_maxed_gates_fill(self) -> None:
        self.options = {
            "min_stages_req_for_castle": 17,
            "max_stages_req_for_castle": 17,
            "min_stages_req_for_submarine_shrine": 12,
            "max_stages_req_for_submarine_shrine": 12,
            "min_stages_req_for_pyramid": 12,
            "max_stages_req_for_pyramid": 12,
            "min_stages_req_for_ice_castle": 14,
            "max_stages_req_for_ice_castle": 14,
            "min_stages_req_for_hell_castle": 22,
            "max_stages_req_for_hell_castle": 22,
            "shuffle_books": 1,
            "shuffle_enemies": 3,
        }
        self.world_setup()
        self.assertSeedWorks()


class TestProgressiveShop(SweepTestBase):
    def test_one_track_per_shop(self) -> None:
        """Each shop gets enough of its own item to open its deepest column."""
        self.options = {"progressive_shop": 1, "shop_checks": 1, "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        counts = self.pool_counts()
        for town, name in PROGRESSIVE_SHOPS.items():
            self.assertEqual(counts[name], PROGRESSIVE_SHOP_COUNTS[town], name)
        self.assertSeedWorks()

    def test_absent_when_the_option_is_off(self) -> None:
        self.options = {"progressive_shop": 0, "shop_checks": 1}
        self.world_setup()
        for name in PROGRESSIVE_SHOPS.values():
            self.assertEqual(self.pool_counts()[name], 0, name)

    def test_ignored_without_shop_checks(self) -> None:
        """
        Nothing in logic sits behind a shop row then, so the items would only
        gate the player's own shop -- and on a books-only seed they did not even
        fit, leaving the deepest rows unopenable. The client is told 0.
        """
        self.options = {"progressive_shop": 1, "shuffle_books": 1, "shuffle_enemies": 0}
        self.world_setup()
        for name in PROGRESSIVE_SHOPS.values():
            self.assertEqual(self.pool_counts()[name], 0, name)
        self.assertEqual(self.world.fill_slot_data()["progressive_shop"], 0)
        self.assertSeedWorks()


class TestShopChecks(SweepTestBase):
    def test_every_shop_item_is_a_check(self) -> None:
        self.options = {"shop_checks": 1, "shuffle_books": 1, "shuffle_enemies": 0}
        self.world_setup()
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        for entry in shop_table.values():
            self.assertIn(entry["name"], names)
        self.assertSeedWorks()

    def test_absent_when_the_option_is_off(self) -> None:
        self.options = {"shop_checks": 0, "shuffle_books": 1}
        self.world_setup()
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertEqual(names & {entry["name"] for entry in shop_table.values()}, set())

    def test_shop_only_seed_is_allowed(self) -> None:
        """Shop checks alone are a valid source; 462 locations is plenty."""
        self.options = {"shop_checks": 1, "shuffle_books": 0, "shuffle_enemies": 0}
        self.world_setup()
        self.assertSeedWorks()

    def test_town_unlocks_become_progression(self) -> None:
        """They gate shop checks now, so fill has to treat them as required."""
        self.options = {"shop_checks": 1, "shuffle_books": 1}
        self.world_setup()
        for unlock in SHOP_TOWN_UNLOCKS.values():
            item = next(i for i in self.multiworld.itempool if i.name == unlock)
            self.assertTrue(item.advancement, f"{unlock} gates shop checks but is not progression")

    def test_town_unlocks_stay_useful_without_shop_checks(self) -> None:
        self.options = {"shop_checks": 0, "shuffle_books": 1}
        self.world_setup()
        for unlock in SHOP_TOWN_UNLOCKS.values():
            item = next(i for i in self.multiworld.itempool if i.name == unlock)
            self.assertFalse(item.advancement, f"{unlock} gates nothing but is progression")

    def test_optional_town_shops_need_their_unlock(self) -> None:
        self.options = {"shop_checks": 1, "shuffle_books": 1}
        self.world_setup()
        for town, unlock in SHOP_TOWN_UNLOCKS.items():
            sold_here = [e["name"] for e in shop_table.values() if e["region"] == town]
            if not sold_here:
                continue
            with self.subTest(town=town):
                every_unlock = [f"Unlock {r}" for r in ("Village", "Resort", "Island")]
                state = self.state_with(*[u for u in every_unlock if u != unlock])
                self.assertFalse(
                    self.can_reach(town, state), f"{town} shop is reachable without {unlock}"
                )


class TestProgressiveShopGatesChecks(SweepTestBase):
    TOWNS = ("Village", "Resort", "Island")

    def test_a_row_needs_its_progressive_items(self) -> None:
        """A tier below the first boss gate needs only the Progressive Shop items."""
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        gated_at = min(threshold for threshold, _ in SHOP_TIER_GATES)
        late = max(
            (e for e in shop_table.values() if 0 < e.get("tier", 0) < gated_at),
            key=lambda e: e["tier"],
        )
        item = PROGRESSIVE_SHOPS[late["region"]]

        location = self.multiworld.get_location(late["name"], self.player)
        state = self.state_with(*[f"Unlock {r}" for r in self.TOWNS])
        for held in range(late["req"]):
            self.assertFalse(
                location.can_reach(state),
                f"{late['name']} (req {late['req']}) reachable with {held} {item}",
            )
            state.collect(self.world.create_item(item), prevent_sweep=True)
        self.assertTrue(location.can_reach(state))

    def test_a_deep_row_needs_the_world_open_too(self) -> None:
        """
        The shop only stocks a deep row once the world has opened that far, so
        every Progressive Shop item in the pool is still not enough on its own.

        Without this the fill treats all 264 Town checks as open from the start
        and is free to bury the stage unlocks behind a wall of Progressive Shop.
        """
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        deepest = max(shop_table.values(), key=lambda e: e.get("tier", 0))
        location = self.multiworld.get_location(deepest["name"], self.player)

        state = self.state_with(*[f"Unlock {r}" for r in self.TOWNS])
        for town, name in PROGRESSIVE_SHOPS.items():
            for _ in range(PROGRESSIVE_SHOP_COUNTS[town]):
                state.collect(self.world.create_item(name), prevent_sweep=True)
        self.assertFalse(
            location.can_reach(state),
            f"{deepest['name']} (tier {deepest['tier']}) is reachable with no stage progress",
        )
        self.assertTrue(location.can_reach(self.multiworld.get_all_state(False)))

    def test_town_opens_its_first_row_for_free(self) -> None:
        """Town is the one shop that starts with something in stock."""
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        opening = next(e for e in shop_table.values() if e["region"] == "Town" and e["req"] == 0)
        location = self.multiworld.get_location(opening["name"], self.player)
        self.assertTrue(location.can_reach(self.state_with()))

    def test_the_other_shops_start_empty(self) -> None:
        """Village, Resort and Island stock nothing until their first item arrives."""
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        for region in ("Village", "Resort", "Island"):
            cheapest = min(
                (e for e in shop_table.values() if e["region"] == region),
                key=lambda e: e["req"],
            )
            self.assertGreater(cheapest["req"], 0, f"{region} still opens for free")
            location = self.multiworld.get_location(cheapest["name"], self.player)
            state = self.state_with(*[f"Unlock {r}" for r in self.TOWNS])
            self.assertFalse(
                location.can_reach(state),
                f"{cheapest['name']} is reachable before any {PROGRESSIVE_SHOPS[region]}",
            )

    def test_a_deep_town_row_waits_for_a_late_stage(self) -> None:
        """
        With Progressive Shop off, Town stocks a row only once a stage with a
        Shop_Reqs entry above it can be beaten -- the deepest row wants the
        last entry in the table, which is Hell Gate.
        """
        self.options = {"shop_checks": 1, "shuffle_books": 1}
        self.world_setup()
        deepest = max(
            (e for e in shop_table.values() if e["region"] == "Town"), key=lambda e: e["tier"]
        )
        location = self.multiworld.get_location(deepest["name"], self.player)
        state = self.state_with(*[f"Unlock {r}" for r in self.TOWNS])
        self.assertFalse(
            location.can_reach(state),
            f"{deepest['name']} is reachable the moment you can walk into the town",
        )
        self.assertTrue(location.can_reach(self.multiworld.get_all_state(False)))

    def test_progressive_shop_is_progression_with_checks_on(self) -> None:
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        for name in PROGRESSIVE_SHOPS.values():
            item = next(i for i in self.multiworld.itempool if i.name == name)
            self.assertTrue(item.advancement, name)

    def test_both_options_together_fill(self) -> None:
        self.options = {
            "shop_checks": 1,
            "progressive_shop": 1,
            "shuffle_books": 1,
            "shuffle_enemies": 3,
            "trap_percentage": 100,
        }
        self.world_setup()
        self.assertSeedWorks()


class TestTownStockRule(SweepTestBase):
    """
    With Progressive Shop off the shop rule is the game's own Shop_Reqs table.

    Row 8 of Town needs a stage with an entry of 9 or more beaten, and the
    cheapest of those is Cavern 1, a Grassland stage behind no gate. Grassland 7
    has an entry of 7, so it opens rows 0-6 only. The other three shops stock
    everything on arrival, so their checks need nothing but the town unlock.
    """

    options = {"shop_checks": 1, "shuffle_books": 1}

    def town_row(self, row: int) -> str:
        return next(e["name"] for e in shop_table.values() if e["region"] == "Town" and e["tier"] == row)

    def test_row_eight_opens_on_cavern_one(self) -> None:
        location = self.multiworld.get_location(self.town_row(8), self.player)
        self.assertFalse(location.can_reach(self.state_with("Unlock Grassland 7")))
        self.assertTrue(location.can_reach(self.state_with("Unlock Cavern 1")))

    def test_row_one_is_free(self) -> None:
        """Opening Street's entry is 2, and it needs no unlock."""
        location = self.multiworld.get_location(self.town_row(1), self.player)
        self.assertTrue(location.can_reach(self.state_with()))

    def test_row_nine_needs_a_sea_stage(self) -> None:
        """Every entry of 10 or more belongs to a stage behind the Castle gate."""
        location = self.multiworld.get_location(self.town_row(9), self.player)
        grassland = self.state_with("Unlock Castle", *unlocks_by_region["Grassland"])
        self.assertFalse(location.can_reach(grassland))
        with_sea = self.state_with("Unlock Castle", "Unlock Seaside 1", *unlocks_by_region["Grassland"])
        self.assertTrue(location.can_reach(with_sea))

    def test_the_other_shops_need_only_their_unlock(self) -> None:
        for town in ("Village", "Resort", "Island"):
            deepest = max(
                (e for e in shop_table.values() if e["region"] == town), key=lambda e: e["tier"]
            )
            location = self.multiworld.get_location(deepest["name"], self.player)
            self.assertTrue(
                location.can_reach(self.state_with(f"Unlock {town}")),
                f"{deepest['name']} should be stocked the moment you can walk in",
            )


class TestShopReqsPin(SweepTestBase):
    """SHOP_REQS is a copy of Shop_Reqs in game.js; drift would strand seeds."""

    options = {"shop_checks": 1, "shuffle_books": 1}

    def test_one_entry_per_stage(self) -> None:
        self.assertEqual(len(SHOP_REQS), 90)


class TestStockingRuleNeverStrands(SweepTestBase):
    """
    Fill real seeds, then sweep them under the game's own stocking rule rather
    than the access rules, and demand the goal is still reachable.

    This is the failure that shipped in 1.8.5: the access rule was looser than
    the shop, so a fill Archipelago called beatable could not be beaten.
    """

    def game_stocked(self, location, state, progressive: bool) -> bool:
        data = shop_by_name.get(location.name)
        if data is None:
            return True
        if progressive:
            return state.count(PROGRESSIVE_SHOPS[data["region"]], self.player) >= data["req"]
        if data["region"] != "Town":
            return True
        level = 1
        for name in regions:
            if self.multiworld.get_region(name, self.player).can_reach(state):
                level = max(level, SHOP_REQS[region_stage_id(name)])
        return data["tier"] < level

    def sweep_like_the_game(self, progressive: bool) -> bool:
        state = CollectionState(self.multiworld)
        collected: set = set()
        while True:
            progressed = False
            for location in self.multiworld.get_locations(self.player):
                if location in collected or not location.can_reach(state):
                    continue
                if not self.game_stocked(location, state, progressive):
                    continue
                collected.add(location)
                state.collect(location.item, prevent_sweep=True)
                progressed = True
            if not progressed:
                return self.multiworld.completion_condition[self.player](state)

    def test_filled_seeds_are_beatable_under_the_game_rule(self) -> None:
        for progressive in (0, 1):
            for seed in (1, 2, 3):
                with self.subTest(progressive_shop=progressive, seed=seed):
                    self.options = {"shop_checks": 1, "shuffle_books": 1, "progressive_shop": progressive}
                    self.world_setup(seed=seed)
                    distribute_items_restrictive(self.multiworld)
                    self.assertTrue(self.sweep_like_the_game(bool(progressive)))


def visible_option_names() -> list[str]:
    """Every option a player can set, in yaml order, minus the rolled hidden ones."""
    return [
        name
        for name, option in SROptions.type_hints.items()
        if name not in PerGameCommonOptions.type_hints and option.visibility is not Visibility.none
    ]


class TestOptionLayout(SweepTestBase):
    """Every option a player sets sits in exactly one group on the options page."""

    def grouped_names(self) -> list[str]:
        """Archipelago appends its own item and location group to the list, so skip what is not ours."""
        names = {
            option: name
            for name, option in SROptions.type_hints.items()
            if name not in PerGameCommonOptions.type_hints
        }
        return [names[option] for group in SR_OPTION_GROUPS for option in group.options if option in names]

    def test_every_visible_option_is_grouped_once(self) -> None:
        """Goal is the one exception: it sits in Archipelago's own top group."""
        grouped = self.grouped_names()
        self.assertEqual(len(grouped), len(set(grouped)), "an option is in two groups")
        self.assertEqual(sorted(grouped), sorted(n for n in visible_option_names() if n != "goal"))

    def test_the_yaml_follows_the_page(self) -> None:
        """The template is written in field order, so that order is the page's."""
        yaml_order = list(SROptions.type_hints)
        positions = [yaml_order.index(name) for name in self.grouped_names()]
        self.assertEqual(positions, sorted(positions), "the yaml and the options page disagree on order")
        self.assertEqual(visible_option_names()[0], "goal")


class TestSlotData(SweepTestBase):
    """Every option the client acts on has to actually reach it.

    An option can be wired through generation perfectly and still do nothing,
    because the client only ever sees slot_data. Shop Checks shipped that way in
    1.7.0: the locations existed, so players saw them in the tracker and filled
    them by hand, but the client read the absent key as off and never sent one.
    """

    def shipped_options(self) -> set[str]:
        """Option names in slot_data that the client is expected to act on.

        The bounds the stage gates are rolled between stay out on purpose; the
        rolled result ships instead. Archipelago's own common options stay out
        because the server applies them, and the hidden 1.8 yaml keys stay out
        because generate_early folds them into the options that replaced them.
        """
        return {
            name
            for name in SROptions.type_hints
            if not name.startswith(("min_stages_req_", "max_stages_req_"))
            and name not in PerGameCommonOptions.type_hints
            and name not in LEGACY_OPTIONS
        }

    def test_every_option_reaches_the_client(self) -> None:
        slot_data = self.world.fill_slot_data()
        for name in sorted(self.shipped_options()):
            self.assertIn(name, slot_data, f"{name} never reaches the client")

    def test_the_named_list_is_complete(self) -> None:
        """SLOT_DATA_OPTIONS is what the client pins, so it has to be the whole set."""
        self.assertEqual(set(SLOT_DATA_OPTIONS), self.shipped_options())
        self.assertEqual(len(SLOT_DATA_OPTIONS), len(set(SLOT_DATA_OPTIONS)), "duplicate key")

    def test_shop_checks_ships_when_off(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["shop_checks"], 0)

    def test_the_world_version_is_the_manifest_version(self) -> None:
        """The client branches on this, so it has to be the number on the tag."""
        manifest = json.loads(
            (Path(__file__).resolve().parents[1] / "archipelago.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.world.fill_slot_data()["world_version"], manifest["world_version"])


class TestSlotDataWithShopChecks(SweepTestBase):
    options = {"shop_checks": 1}

    def test_shop_checks_ships_when_on(self) -> None:
        """The value has to survive, not just the key: the client treats a
        missing or zero value as the feature being off."""
        self.assertEqual(self.world.fill_slot_data()["shop_checks"], 1)


class TestEnforceShopLogic(SweepTestBase):
    """The option only changes what the client allows, never what fills."""

    options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1, "enforce_shop_logic": 1}

    def test_the_client_is_told(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["enforce_shop_logic"], 1)

    def test_ignored_without_shop_checks(self) -> None:
        """There is no shop logic to enforce then, so the client must not grey anything."""
        self.options = {"shuffle_books": 1, "enforce_shop_logic": 1}
        self.world_setup()
        self.assertEqual(self.world.fill_slot_data()["enforce_shop_logic"], 0)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()

    def test_shop_gates_name_a_real_boss_stage(self) -> None:
        """Each threshold points at a gate the client can actually evaluate."""
        logic = self.world.fill_slot_data()["logic"]
        gate_stages = {gate["stage"] for gate in logic["gates"]}
        self.assertEqual(len(logic["shop_gates"]), len(SHOP_TIER_GATES))
        for threshold, stage in logic["shop_gates"]:
            self.assertIn(stage, gate_stages, f"tier {threshold} points at no known gate")

    def test_shop_gates_are_highest_first(self) -> None:
        """The client returns on the first match, so order decides the answer."""
        thresholds = [threshold for threshold, _ in self.world.fill_slot_data()["logic"]["shop_gates"]]
        self.assertEqual(thresholds, sorted(thresholds, reverse=True))

    def test_gates_match_the_rules(self) -> None:
        """What the client enforces is what set_shop_rules used."""
        shipped = {t: s for t, s in self.world.fill_slot_data()["logic"]["shop_gates"]}
        expected = {t: stage_id(boss) for t, boss in SHOP_TIER_GATES}
        self.assertEqual(shipped, expected)


class TestRingGold(SweepTestBase):
    """Ring Gold is Ring Link's payout, so it is zeroed without it."""

    options = {"shuffle_books": 1, "ring_link": 1, "ring_gold": 50}

    def test_ships_with_ring_link(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["ring_gold"], 50)

    def test_zeroed_without_ring_link(self) -> None:
        self.options = {"shuffle_books": 1, "ring_link": 0, "ring_gold": 50}
        self.world_setup()
        self.assertEqual(self.world.fill_slot_data()["ring_gold"], 0)


class TestShopHints(SweepTestBase):
    """Purely a client instruction: it must reach the client and change nothing else."""

    options = {"shuffle_books": 1, "shop_checks": 1, "shop_hints": "important_only"}

    def test_the_client_is_told(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["shop_hints"], ShopHints.option_important_only)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()

    def test_it_does_not_touch_the_item_pool(self) -> None:
        """Hint filtering is presentation, so the seed must be identical without it."""
        quiet = self.pool_counts()
        self.options = {"shuffle_books": 1, "shop_checks": 1, "shop_hints": "all"}
        self.world_setup(seed=self.multiworld.seed)
        self.assertEqual(quiet, self.pool_counts())

    def test_the_old_toggle_values_still_parse(self) -> None:
        """Shop Hints was a toggle until 1.8.12, so yamls out there say true or false."""
        self.assertEqual(ShopHints.from_any("true").value, ShopHints.option_all)
        self.assertEqual(ShopHints.from_any("false").value, ShopHints.option_off)
        self.assertEqual(ShopHints.from_any("important_only").value, ShopHints.option_important_only)


class TestTrapDisguise(SweepTestBase):
    """Presentation only: it reaches the client and changes nothing about the fill."""

    options = {"shuffle_books": 1, "shop_checks": 1, "trap_percentage": 20, "trap_disguise": 1}

    def test_the_client_is_told(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["trap_disguise"], 1)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()

    def test_traps_keep_their_real_names(self) -> None:
        """The disguise is worn in the client, so the pool is untouched."""
        names = {item.name for item in self.multiworld.itempool}
        self.assertTrue(
            names & {trap.item_name for trap in traps},
            "no traps in the pool, so this proves nothing",
        )


class TestRemovableCompos(SweepTestBase):
    """A client rule about the inventory: it ships, and the fill is untouched."""

    options = {"shuffle_books": 1, "removable_compos": 1}

    def test_the_client_is_told(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["removable_compos"], 1)

    def test_it_is_off_by_default(self) -> None:
        """The base game fits a compo for good, so nothing changes unasked."""
        self.options = {"shuffle_books": 1}
        self.world_setup()
        self.assertEqual(self.world.fill_slot_data()["removable_compos"], 0)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()


class TestShopLocationNames(SweepTestBase):
    """A shop check says which town it is in, so a hint tells you where to go."""

    options = {"shop_checks": 1, "shuffle_books": 1}

    def test_every_name_says_its_town(self) -> None:
        for entry in shop_table.values():
            self.assertTrue(
                entry["name"].startswith(f"{entry['region']} Shop: "),
                f"{entry['name']} does not say it is in {entry['region']}",
            )

    def test_names_are_unique(self) -> None:
        """The table is keyed by id, but Archipelago looks locations up by name."""
        names = [entry["name"] for entry in shop_table.values()]
        self.assertEqual(len(names), len(set(names)))

    def test_every_town_is_represented(self) -> None:
        towns = {entry["region"] for entry in shop_table.values()}
        self.assertEqual(towns, {"Town", "Village", "Resort", "Island"})

    def test_the_world_can_find_them_all(self) -> None:
        """Renaming breaks generation outright if anything still used the old name."""
        for entry in shop_table.values():
            self.multiworld.get_location(entry["name"], self.player)


class TestProgressiveShopCounts(SweepTestBase):
    """Each track is as long as its shop needs and no longer."""

    options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}

    def test_every_check_is_reachable_with_the_pool(self) -> None:
        """A check asking for more items than exist could never be bought."""
        for entry in shop_table.values():
            self.assertLessEqual(
                entry["req"],
                PROGRESSIVE_SHOP_COUNTS[entry["region"]],
                f"{entry['name']} needs {entry['req']} of a track only {PROGRESSIVE_SHOP_COUNTS[entry['region']]} long",
            )

    def test_resort_opens_on_one_item(self) -> None:
        """
        Resort stocks two items per column and the grid shows both on its first
        row, so the shop has a single stock level. Sizing the track to the nine
        deep columns instead put eight items in the pool that opened nothing.
        """
        self.assertEqual(PROGRESSIVE_SHOP_COUNTS["Resort"], 1)
        self.assertEqual(SHOP_PROGRESSION_STEPS["Resort"], 1)

    def test_a_track_covers_its_own_deepest_check(self) -> None:
        """The pool has to be able to reach the last row that holds a check."""
        for town, count in PROGRESSIVE_SHOP_COUNTS.items():
            deepest = max(
                (e["req"] for e in shop_table.values() if e["region"] == town),
                default=0,
            )
            self.assertGreaterEqual(count, deepest, f"{town} cannot reach its own deepest check")

    def test_no_track_is_empty(self) -> None:
        for town, count in PROGRESSIVE_SHOP_COUNTS.items():
            self.assertGreater(count, 0, f"{town} would never open past its first row")


class TestBookCostTenth(SweepTestBase):
    """The cheap mode is a Book Cost Randomizer value, not an option of its own."""

    options = {"shuffle_books": 1, "randomize_book_costs": 4}

    def test_the_client_is_told_which_mode(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["randomize_book_costs"], 4)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()

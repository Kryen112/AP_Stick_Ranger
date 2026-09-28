"""Generation sweeps: every goal and every check-source combination has to fill
and stay beatable."""

from __future__ import annotations

from collections import Counter

from Options import OptionError, PerGameCommonOptions

from ..constants import GOAL_OPTIONS_MAP
from ..items import PROGRESSIVE_SHOP_COUNTS, PROGRESSIVE_SHOPS, SHOP_TOWN_UNLOCKS, traps
from ..items import stage_id
from ..rules import SHOP_TIER_GATES
from ..options import SROptions
from ..shop import shop_table
from . import StickRangerTestBase


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
        for traps in range(6):   # none, 5, 10, 20, 50, 100
            with self.subTest(traps=traps):
                self.options = {"traps": traps, "shuffle_books": 1, "shuffle_enemies": 3}
                self.world_setup()
                self.assertSeedWorks()
                trap_count = sum(1 for item in self.multiworld.itempool if item.trap)
                if traps == 0:
                    self.assertEqual(trap_count, 0)
                else:
                    self.assertGreater(trap_count, 0)


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
        self.options = {"progressive_shop": 1, "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        counts = self.pool_counts()
        for town, name in PROGRESSIVE_SHOPS.items():
            self.assertEqual(counts[name], PROGRESSIVE_SHOP_COUNTS[town], name)
        self.assertSeedWorks()

    def test_absent_when_the_option_is_off(self) -> None:
        self.options = {"progressive_shop": 0}
        self.world_setup()
        for name in PROGRESSIVE_SHOPS.values():
            self.assertEqual(self.pool_counts()[name], 0, name)

    def test_fits_the_smallest_pool(self) -> None:
        """89 extra items still has to fit a books-only seed."""
        self.options = {"progressive_shop": 1, "shuffle_books": 1, "shuffle_enemies": 0}
        self.world_setup()
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

    def test_shop_tiers_are_gated_without_progressive_shop(self) -> None:
        """
        With Progressive Shop off the game still widens the stock as stages are
        beaten, so the tier gates have to apply on their own.
        """
        self.options = {"shop_checks": 1, "shuffle_books": 1}
        self.world_setup()
        deepest = max(shop_table.values(), key=lambda e: e.get("tier", 0))
        location = self.multiworld.get_location(deepest["name"], self.player)
        state = self.state_with(*[f"Unlock {r}" for r in self.TOWNS])
        self.assertFalse(
            location.can_reach(state),
            f"{deepest['name']} is reachable the moment you can walk into the town",
        )

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
            "traps": 5,
        }
        self.world_setup()
        self.assertSeedWorks()



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
        because the server applies them.
        """
        return {
            name
            for name in SROptions.type_hints
            if not name.startswith(("min_stages_req_", "max_stages_req_"))
            and name not in PerGameCommonOptions.type_hints
        }

    def test_every_option_reaches_the_client(self) -> None:
        slot_data = self.world.fill_slot_data()
        for name in sorted(self.shipped_options()):
            self.assertIn(name, slot_data, f"{name} never reaches the client")

    def test_shop_checks_ships_when_off(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["shop_checks"], 0)


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


class TestImportantHintsOnly(SweepTestBase):
    """Purely a client instruction: it must reach the client and change nothing else."""

    options = {"shuffle_books": 1, "shop_checks": 1, "important_hints_only": 1}

    def test_the_client_is_told(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["important_hints_only"], 1)

    def test_the_seed_still_fills(self) -> None:
        self.assertSeedWorks()

    def test_it_does_not_touch_the_item_pool(self) -> None:
        """Hint filtering is presentation, so the seed must be identical without it."""
        quiet = self.pool_counts()
        self.options = {"shuffle_books": 1, "shop_checks": 1, "important_hints_only": 0}
        self.world_setup(seed=self.multiworld.seed)
        self.assertEqual(quiet, self.pool_counts())


class TestTrapDisguise(SweepTestBase):
    """Presentation only: it reaches the client and changes nothing about the fill."""

    options = {"shuffle_books": 1, "shop_checks": 1, "traps": 20, "trap_disguise": 1}

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

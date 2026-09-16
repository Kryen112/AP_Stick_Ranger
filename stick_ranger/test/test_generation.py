"""Generation sweeps: every goal and every check-source combination has to fill
and stay beatable."""

from __future__ import annotations

from collections import Counter

from Options import OptionError

from ..constants import GOAL_OPTIONS_MAP
from ..items import PROGRESSIVE_SHOP, PROGRESSIVE_SHOP_TIERS, SHOP_TOWN_UNLOCKS
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
    def test_one_item_per_shop_tier(self) -> None:
        self.options = {"progressive_shop": 1, "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        self.assertEqual(self.pool_counts()[PROGRESSIVE_SHOP], PROGRESSIVE_SHOP_TIERS)
        self.assertSeedWorks()

    def test_absent_when_the_option_is_off(self) -> None:
        self.options = {"progressive_shop": 0}
        self.world_setup()
        self.assertEqual(self.pool_counts()[PROGRESSIVE_SHOP], 0)

    def test_fits_the_smallest_pool(self) -> None:
        """33 extra items still has to fit a books-only seed."""
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
    def test_a_late_row_needs_its_progressive_items(self) -> None:
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        late = max(shop_table.values(), key=lambda e: e.get("tier", 0))
        tier = late["tier"]
        self.assertGreater(tier, 0)

        location = self.multiworld.get_location(late["name"], self.player)
        state = self.state_with(*[f"Unlock {r}" for r in ("Village", "Resort", "Island")])
        for held in range(tier):
            self.assertFalse(
                location.can_reach(state),
                f"{late['name']} (tier {tier}) reachable with {held} Progressive Shop",
            )
            state.collect(self.world.create_item(PROGRESSIVE_SHOP), prevent_sweep=True)
        self.assertTrue(location.can_reach(state))

    def test_progressive_shop_is_progression_with_checks_on(self) -> None:
        self.options = {"shop_checks": 1, "progressive_shop": 1, "shuffle_books": 1}
        self.world_setup()
        item = next(i for i in self.multiworld.itempool if i.name == PROGRESSIVE_SHOP)
        self.assertTrue(item.advancement)

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

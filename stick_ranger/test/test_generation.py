"""Generation sweeps: every goal and every check-source combination has to fill
and stay beatable."""

from __future__ import annotations

from collections import Counter

from Options import OptionError

from ..constants import GOAL_OPTIONS_MAP
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
        for traps in range(5):
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

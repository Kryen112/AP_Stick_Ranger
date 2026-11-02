"""Early goals, what they cut from the seed, and the options that came with them:
Towns in Pool, Surplus Classes and the two loot options."""

from __future__ import annotations

from BaseClasses import CollectionState, LocationProgressType
from Fill import distribute_items_restrictive

from ..constants import GOAL_OPTIONS_MAP, RANGER_CLASSES
from ..goal import GoalScope, loot_tier_cap
from ..items import FILLER_TIER, stage_id, stages
from ..options import HellCastleMaximumStagesUnlocks
from ..regions import regions
from ..shop import shop_table
from . import test_generation
from .test_generation import SweepTestBase

EARLY_GOALS = {"castle": 7, "submarine_shrine": 8, "pyramid": 9, "ice_castle": 10}


def cut_stages(goal: int) -> set[str]:
    scope = GoalScope(goal)
    return {name for name in regions if scope.is_cut(name)}


class GoalTestBase(SweepTestBase):
    def location_names(self) -> set[str]:
        return {location.name for location in self.multiworld.get_locations(self.player)}

    def excluded(self) -> set[str]:
        return {
            location.name
            for location in self.multiworld.get_locations(self.player)
            if location.progress_type is LocationProgressType.EXCLUDED
        }

    def filler_in_pool(self) -> list[str]:
        return [item.name for item in self.multiworld.itempool if item.name in FILLER_TIER]


class TestWhatEachGoalCuts(GoalTestBase):
    def test_the_scope_of_each_early_goal(self) -> None:
        """Pinned by hand, so a change to the depth tables shows up here."""
        self.assertIn("Seaside 1", cut_stages(EARLY_GOALS["castle"]))
        self.assertNotIn("Cavern 3", cut_stages(EARLY_GOALS["castle"]))
        self.assertIn("Desert 1", cut_stages(EARLY_GOALS["submarine_shrine"]))
        self.assertNotIn("???", cut_stages(EARLY_GOALS["submarine_shrine"]))
        self.assertIn("Cavern 4", cut_stages(EARLY_GOALS["pyramid"]))
        self.assertIn("Mountaintop", cut_stages(EARLY_GOALS["pyramid"]))
        self.assertNotIn("Beach 3", cut_stages(EARLY_GOALS["pyramid"]))
        self.assertIn("Snowfield 9", cut_stages(EARLY_GOALS["ice_castle"]))
        self.assertNotIn("!!!", cut_stages(EARLY_GOALS["ice_castle"]))
        self.assertNotIn("Mountaintop", cut_stages(EARLY_GOALS["ice_castle"]))
        self.assertIn("Hell 1", cut_stages(2))   # Mountaintop
        self.assertIn("Hell Castle", cut_stages(2))
        self.assertEqual(cut_stages(0), set())   # Hell Castle

    def test_towns_follow_the_goal(self) -> None:
        castle, sub, pyramid, ice = (GoalScope(v) for v in EARLY_GOALS.values())
        self.assertFalse(castle.is_cut("Village"))
        self.assertTrue(castle.is_cut("Resort"))
        self.assertTrue(sub.is_cut("Resort"))
        self.assertFalse(pyramid.is_cut("Resort"))
        self.assertTrue(ice.is_cut("Island"))
        self.assertFalse(GoalScope(0).is_cut("Island"))
        self.assertFalse(castle.is_cut("Forget Tree"))

    def test_cut_stages_hold_no_checks_and_hand_out_no_unlocks(self) -> None:
        for goal_name, goal in EARLY_GOALS.items():
            with self.subTest(goal=goal_name):
                self.options = {"goal": goal, "shuffle_books": 1, "shuffle_enemies": 3}
                self.world_setup()
                cut = cut_stages(goal)
                pool = self.pool_counts()
                for location in self.multiworld.get_locations(self.player):
                    self.assertNotIn(location.parent_region.name, cut, location.name)
                for stage in cut:
                    self.assertEqual(pool[f"Unlock {stage}"], 0, f"Unlock {stage} is in the pool")
                for unlock in stages:
                    stage = unlock.item_name.removeprefix("Unlock ")
                    if stage not in cut and stage in regions and unlock.region != "Town":
                        self.assertGreaterEqual(
                            pool[unlock.item_name] + (unlock.item_name == self.world.starter_item_name),
                            1,
                            f"{unlock.item_name} went missing",
                        )

    def test_the_tightest_seeds_fill(self) -> None:
        """A Castle goal with one check source is the smallest seed there is."""
        for combination in (
            {"shuffle_books": 1, "shuffle_enemies": 0},
            {"shuffle_books": 0, "shuffle_enemies": 2},
            {"shuffle_books": 0, "shuffle_enemies": 1},
        ):
            with self.subTest(**combination):
                self.options = {"goal": EARLY_GOALS["castle"], "ranger_class_randomizer": 1,
                                **combination}
                self.world_setup()
                self.assertSeedWorks()


class TestSideBosses(GoalTestBase):
    def side_boss_regions_excluded(self, goal: int, expected: set[str]) -> None:
        self.options = {"goal": goal, "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        excluded = self.excluded()
        for location in self.multiworld.get_locations(self.player):
            region = location.parent_region.name
            if region in expected:
                self.assertIn(location.name, excluded)
            else:
                self.assertNotIn(location.name, excluded)

    def test_hell_castle_goal(self) -> None:
        self.side_boss_regions_excluded(0, {"Volcano", "Mountaintop"})

    def test_volcano_goal(self) -> None:
        self.side_boss_regions_excluded(1, {"Hell Castle", "Mountaintop"})

    def test_mountaintop_goal(self) -> None:
        self.side_boss_regions_excluded(2, {"Ice Castle"})

    def test_ice_castle_goal(self) -> None:
        self.side_boss_regions_excluded(EARLY_GOALS["ice_castle"], {"Mountaintop"})

    def test_all_excludes_nothing(self) -> None:
        self.side_boss_regions_excluded(6, set())

    def test_castle_goal_has_no_side_bosses(self) -> None:
        self.side_boss_regions_excluded(EARLY_GOALS["castle"], set())


class TestEarlyGoalShops(GoalTestBase):
    def test_castle_goal_keeps_only_rows_stocked_before_the_sea(self) -> None:
        self.options = {"goal": EARLY_GOALS["castle"], "shop_checks": 1, "progressive_shop": 1}
        self.world_setup()
        names = self.location_names()
        for entry in shop_table.values():
            if entry["region"] in ("Resort", "Island") or entry["tier"] >= 9:
                self.assertNotIn(entry["name"], names)
            else:
                self.assertIn(entry["name"], names)
        pool = self.pool_counts()
        self.assertEqual(pool["Progressive Island Shop"], 0)
        self.assertEqual(pool["Progressive Resort Shop"], 0)
        self.assertEqual(pool["Progressive Town Shop"], 8)
        self.assertEqual(pool["Unlock Resort"], 0)
        self.assertEqual(pool["Unlock Island"], 0)
        self.assertSeedWorks()

    def test_every_goal_fills_with_shop_checks(self) -> None:
        for goal in GOAL_OPTIONS_MAP:
            for progressive in (0, 1):
                with self.subTest(goal=goal, progressive_shop=progressive):
                    self.options = {
                        "goal": goal, "shop_checks": 1, "progressive_shop": progressive,
                        "shuffle_books": 0,
                    }
                    self.world_setup()
                    self.assertSeedWorks()


# Through the module, so the parent is not collected here a second time.
class TestEarlyGoalsUnderTheGameRule(test_generation.TestStockingRuleNeverStrands):
    """The game's own stocking rule, against a seed that cut most of the shop."""

    def test_filled_seeds_are_beatable_under_the_game_rule(self) -> None:
        for goal in EARLY_GOALS.values():
            for progressive in (0, 1):
                with self.subTest(goal=goal, progressive_shop=progressive):
                    self.options = {"goal": goal, "shop_checks": 1, "progressive_shop": progressive}
                    self.world_setup(seed=1)
                    distribute_items_restrictive(self.multiworld)
                    self.assertTrue(self.sweep_like_the_game(bool(progressive)))


class TestTownsInPool(GoalTestBase):
    def test_a_town_left_out_never_opens(self) -> None:
        self.options = {"shop_checks": 1, "progressive_shop": 1, "towns_in_pool": ["Village"]}
        self.world_setup()
        pool = self.pool_counts()
        self.assertEqual(pool["Unlock Village"], 1)
        for town in ("Resort", "Island"):
            self.assertEqual(pool[f"Unlock {town}"], 0)
            self.assertEqual(pool[f"Progressive {town} Shop"], 0)
            for entry in shop_table.values():
                if entry["region"] == town:
                    self.assertNotIn(entry["name"], self.location_names())
        self.assertSeedWorks()

    def test_it_works_without_shop_checks(self) -> None:
        self.options = {"towns_in_pool": []}
        self.world_setup()
        pool = self.pool_counts()
        for town in ("Village", "Resort", "Island"):
            self.assertEqual(pool[f"Unlock {town}"], 0)
        self.assertSeedWorks()

    def test_the_goal_still_wins(self) -> None:
        """A town past the goal is out, whatever the option says."""
        self.options = {"goal": EARLY_GOALS["castle"], "towns_in_pool": ["Village", "Island"]}
        self.world_setup()
        self.assertEqual(self.pool_counts()["Unlock Island"], 0)


class TestSurplusClasses(GoalTestBase):
    def class_items(self) -> list[str]:
        return [name for name in self.pool_counts().elements() if name.endswith(" Class")]

    def setup_with(self, mode: str) -> None:
        self.options = {
            "goal": EARLY_GOALS["castle"],
            "ranger_class_randomizer": 1,
            "classes_req_for_castle": 3,
            "surplus_classes": mode,
            "shuffle_books": 1,
        }
        self.world_setup()

    def test_in_pool_keeps_every_class(self) -> None:
        self.setup_with("in_pool")
        self.assertEqual(len(self.class_items()), len(RANGER_CLASSES) - 1)

    def test_removed_keeps_only_what_the_goal_needs(self) -> None:
        self.setup_with("removed")
        self.assertEqual(len(self.class_items()), 2)
        self.assertSeedWorks()

    def test_start_with_hands_over_the_rest(self) -> None:
        self.setup_with("start_with")
        self.assertEqual(len(self.class_items()), 2)
        precollected = [
            item.name for item in self.multiworld.precollected_items[self.player]
            if item.name.endswith(" Class")
        ]
        self.assertEqual(len(precollected), 5)
        self.assertEqual(set(precollected) & set(self.class_items()), set())
        self.assertSeedWorks()

    def test_a_late_goal_reads_its_own_requirement(self) -> None:
        self.options = {
            "goal": "volcano",
            "ranger_class_randomizer": 1,
            "classes_req_for_hell_castle": 5,
            "surplus_classes": "removed",
        }
        self.world_setup()
        self.assertEqual(len(self.class_items()), 4)


class TestCapLootAtGoal(GoalTestBase):
    def test_castle_goal_stays_at_tier_two(self) -> None:
        self.options = {"goal": EARLY_GOALS["castle"], "shuffle_books": 1, "shuffle_enemies": 3}
        self.world_setup()
        self.assertTrue(self.filler_in_pool())
        for name in self.filler_in_pool():
            self.assertLessEqual(FILLER_TIER[name], 2, name)
        for _ in range(50):
            self.assertLessEqual(FILLER_TIER[self.world.get_filler_item_name()], 2)

    def test_each_goal_caps_at_its_own_area(self) -> None:
        caps = {"castle": 2, "submarine_shrine": 3, "pyramid": 5, "ice_castle": 6}
        for goal_name, cap in caps.items():
            self.assertEqual(GoalScope(EARLY_GOALS[goal_name]).loot_tier_cap, cap)
        self.assertEqual(GoalScope(2).loot_tier_cap, 6)   # Mountaintop
        self.assertEqual(GoalScope(0).loot_tier_cap, 8)

    def test_off_lets_anything_through(self) -> None:
        self.options = {"goal": EARLY_GOALS["castle"], "cap_loot_at_goal": 0}
        self.world_setup()
        self.assertEqual(max(FILLER_TIER[name] for name in self.world.filler_names), 8)


class TestScaleLootWithProgress(GoalTestBase):
    def test_filler_never_outruns_its_sphere(self) -> None:
        for seed in (1, 2, 3):
            with self.subTest(seed=seed):
                self.options = {
                    "scale_loot_with_progress": 1,
                    "shuffle_books": 1,
                    "shuffle_enemies": 3,
                }
                self.world_setup(seed=seed)
                distribute_items_restrictive(self.multiworld)
                type(self.world).stage_post_fill(self.multiworld)

                state = CollectionState(self.multiworld)
                remaining = set(self.multiworld.get_filled_locations())
                found_low = False
                while remaining:
                    sphere = {loc for loc in remaining if loc.can_reach(state)}
                    if not sphere:
                        break
                    cap = self.world._loot_cap(state)
                    for location in sphere:
                        name = location.item.name
                        if location.item.player == self.player and name in FILLER_TIER:
                            self.assertLessEqual(FILLER_TIER[name], cap, location.name)
                            found_low = found_low or cap == loot_tier_cap(0)
                    for location in sphere:
                        state.collect(location.item, True, location)
                    remaining -= sphere
                self.assertTrue(found_low, "no filler was judged before Castle opened")
                self.assertTrue(self.multiworld.can_beat_game(CollectionState(self.multiworld)))

    def test_off_leaves_the_fill_alone(self) -> None:
        self.options = {"shuffle_books": 1}
        self.world_setup()
        distribute_items_restrictive(self.multiworld)
        before = {loc.name: loc.item.name for loc in self.multiworld.get_filled_locations()}
        type(self.world).stage_post_fill(self.multiworld)
        after = {loc.name: loc.item.name for loc in self.multiworld.get_filled_locations()}
        self.assertEqual(before, after)


class TestGoalReachesTheClient(GoalTestBase):
    def test_goal_stages_ship(self) -> None:
        for goal, names in GOAL_OPTIONS_MAP.items():
            with self.subTest(goal=goal):
                self.options = {"goal": goal}
                self.world_setup()
                self.assertEqual(
                    self.world.fill_slot_data()["goal_stages"], [stage_id(n) for n in names]
                )

    def test_free_play_opens_what_was_cut(self) -> None:
        self.options = {"goal": EARLY_GOALS["castle"], "towns_in_pool": []}
        self.world_setup()
        free_play = self.world.fill_slot_data()["free_play_stages"]
        expected = {stage_id(name) for name in cut_stages(EARLY_GOALS["castle"])}
        expected |= {stage_id(town) for town in ("Village", "Resort", "Island")}
        self.assertEqual(set(free_play), expected)
        self.assertNotIn(stage_id("Cavern 3"), free_play)

    def test_free_play_is_empty_when_nothing_is_cut(self) -> None:
        self.options = {"goal": "hell_castle"}
        self.world_setup()
        self.assertEqual(self.world.fill_slot_data()["free_play_stages"], [])

    def test_logic_stops_at_the_goal(self) -> None:
        self.options = {"goal": EARLY_GOALS["castle"]}
        self.world_setup()
        logic = self.world.fill_slot_data()["logic"]
        self.assertEqual([g["stage"] for g in logic["gates"]], [stage_id("Castle")])
        self.assertEqual(logic["boss_rush"], [])

    def test_mountaintop_goal_keeps_its_sibling_gate(self) -> None:
        self.options = {"goal": "mountaintop"}
        self.world_setup()
        gates = [g["stage"] for g in self.world.fill_slot_data()["logic"]["gates"]]
        self.assertIn(stage_id("Ice Castle"), gates)
        self.assertIn(stage_id("Mountaintop"), gates)
        self.assertNotIn(stage_id("Hell Castle"), gates)


class TestOldYamls(GoalTestBase):
    def test_a_hell_count_of_22_still_parses(self) -> None:
        """!!! moved to the Ice region, so 22 Hell stages is now 21."""
        self.assertEqual(HellCastleMaximumStagesUnlocks.from_any(22).value, 21)
        self.assertEqual(HellCastleMaximumStagesUnlocks.from_text("22").value, 21)
        self.assertEqual(HellCastleMaximumStagesUnlocks.from_any(12).value, 12)

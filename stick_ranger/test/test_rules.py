"""The access rules, and the slot_data the client gates its map colouring on."""

from __future__ import annotations

from BaseClasses import CollectionState, LocationProgressType

from ..constants import CLASS_REQ_OPTIONS
from ..items import classes, unlocks_by_region
from ..regions import regions
from . import StickRangerTestBase

BOSS_CHAIN = ["Castle", "Submarine Shrine", "Pyramid", "Ice Castle", "Hell Castle"]


class TestEveryStageNeedsItsUnlock(StickRangerTestBase):
    """No stage but Opening Street may be reachable without its own unlock."""

    options = {"shuffle_books": 1, "shuffle_enemies": 3}

    def test_own_unlock_required(self) -> None:
        every_unlock = [f"Unlock {region}" for region in regions if region != "Opening Street"]
        every_class = [item.item_name for item in classes]
        for held_back in every_unlock:
            with self.subTest(region=held_back):
                # A state built from scratch each time -- collect_all_but leaves
                # the previous subtest's items behind.
                state = CollectionState(self.multiworld)
                for name in every_unlock + every_class:
                    if name != held_back:
                        state.collect(self.world.create_item(name), prevent_sweep=True)
                region = held_back.removeprefix("Unlock ")
                self.assertFalse(
                    self.multiworld.get_region(region, self.player).can_reach(state),
                    f"{region} is reachable without {held_back}",
                )


class TestBossChain(StickRangerTestBase):
    """Each boss gate has to wait for the one before it."""

    options = {
        "ranger_class_randomizer": 0,
        "min_stages_req_for_castle": 0,
        "max_stages_req_for_castle": 0,
        "min_stages_req_for_submarine_shrine": 0,
        "max_stages_req_for_submarine_shrine": 0,
        "min_stages_req_for_pyramid": 0,
        "max_stages_req_for_pyramid": 0,
        "min_stages_req_for_ice_castle": 0,
        "max_stages_req_for_ice_castle": 0,
        "min_stages_req_for_hell_castle": 0,
        "max_stages_req_for_hell_castle": 0,
    }

    def state_with(self, *item_names: str) -> CollectionState:
        """A state holding exactly these items, independent of any other subtest."""
        state = CollectionState(self.multiworld)
        for item_name in item_names:
            state.collect(self.world.create_item(item_name), prevent_sweep=True)
        return state

    def test_each_boss_waits_for_the_previous_one(self) -> None:
        for index, missing in enumerate(BOSS_CHAIN):
            with self.subTest(missing=missing):
                state = self.state_with(
                    *[f"Unlock {name}" for name in BOSS_CHAIN if name != missing]
                )
                for blocked in BOSS_CHAIN[index:]:
                    self.assertFalse(
                        self.multiworld.get_region(blocked, self.player).can_reach(state),
                        f"{blocked} opened without Unlock {missing}",
                    )
                for open_stage in BOSS_CHAIN[:index]:
                    self.assertTrue(
                        self.multiworld.get_region(open_stage, self.player).can_reach(state),
                        f"{open_stage} should not care about Unlock {missing}",
                    )

    def test_boss_rush_stages_wait_for_hell_castle(self) -> None:
        for boss_rush in ("Volcano", "Mountaintop"):
            with self.subTest(stage=boss_rush):
                whole_chain = [f"Unlock {name}" for name in BOSS_CHAIN]
                region = self.multiworld.get_region(boss_rush, self.player)
                self.assertTrue(
                    region.can_reach(self.state_with(*whole_chain, f"Unlock {boss_rush}"))
                )
                self.assertFalse(
                    region.can_reach(self.state_with(*whole_chain)),
                    f"{boss_rush} opened without its own unlock",
                )
                self.assertFalse(
                    region.can_reach(
                        self.state_with(*whole_chain[:-1], f"Unlock {boss_rush}")
                    ),
                    f"{boss_rush} opened without Unlock Hell Castle",
                )


class TestStageThresholds(StickRangerTestBase):
    """The Castle gate counts Grassland unlocks, and nothing else."""

    options = {
        "ranger_class_randomizer": 0,
        "min_stages_req_for_castle": 5,
        "max_stages_req_for_castle": 5,
    }

    def test_castle_needs_five_grassland_unlocks(self) -> None:
        self.collect_items("Unlock Castle")
        grassland = unlocks_by_region["Grassland"]
        for held in range(5):
            self.assertFalse(
                self.can_reach_region("Castle"),
                f"Castle opened on {held} Grassland unlocks, needs 5",
            )
            self.collect_items(grassland[held])
        self.assertTrue(self.can_reach_region("Castle"))

    def test_other_regions_do_not_count(self) -> None:
        self.collect_items("Unlock Castle", *unlocks_by_region["Sea"], *unlocks_by_region["Hell"])
        self.assertFalse(self.can_reach_region("Castle"))


class TestClassGate(StickRangerTestBase):
    """The class gate counts the starting class, as class_count() documents."""

    options = {
        "ranger_class_randomizer": 1,
        "ranger_class_selected": "boxer",
        "classes_req_for_castle": 3,
        "min_stages_req_for_castle": 0,
        "max_stages_req_for_castle": 0,
    }

    def test_starting_class_counts(self) -> None:
        self.collect_items("Unlock Castle")
        self.assertFalse(self.can_reach_region("Castle"), "1 class should not satisfy 3")
        self.collect_items("Unlock Sniper Class")
        self.assertFalse(self.can_reach_region("Castle"), "2 classes should not satisfy 3")
        self.collect_items("Unlock Angel Class")
        self.assertTrue(self.can_reach_region("Castle"), "start + 2 unlocks is 3")


class TestClassRequirementsResolved(StickRangerTestBase):
    """
    Whatever the rules gate on has to be what slot_data ships, or the client
    colours the map against numbers the generator never used.
    """

    options = {
        "ranger_class_randomizer": 0,
        "classes_req_for_castle": 4,
        "classes_req_for_hell_castle": 6,
    }

    def test_class_randomizer_off_zeroes_every_gate(self) -> None:
        slot_data = self.multiworld.worlds[1].fill_slot_data()
        for option_name in CLASS_REQ_OPTIONS:
            self.assertEqual(getattr(self.world.options, option_name).value, 0)
            self.assertEqual(slot_data[option_name], 0)


class TestClassRequirementsClamped(StickRangerTestBase):
    options = {
        "ranger_class_randomizer": 1,
        "classes_req_for_castle": 5,
        "classes_req_for_submarine_shrine": 2,
        "classes_req_for_pyramid": 3,
        "classes_req_for_ice_castle": 1,
        "classes_req_for_hell_castle": 6,
    }

    def test_gates_never_decrease(self) -> None:
        resolved = [getattr(self.world.options, name).value for name in CLASS_REQ_OPTIONS]
        self.assertEqual(resolved, [5, 5, 5, 5, 6])
        slot_data = self.multiworld.worlds[1].fill_slot_data()
        self.assertEqual([slot_data[name] for name in CLASS_REQ_OPTIONS], resolved)


class TestSlotDataStageRequirements(StickRangerTestBase):
    options = {
        "min_stages_req_for_castle": 3,
        "max_stages_req_for_castle": 9,
    }

    def test_rolled_value_lands_in_range_and_ships(self) -> None:
        slot_data = self.multiworld.worlds[1].fill_slot_data()
        rolled = slot_data["stages_req_for_castle"]
        self.assertGreaterEqual(rolled, 3)
        self.assertLessEqual(rolled, 9)
        self.assertEqual(rolled, self.world.options.stages_req_for_castle.value)

    def test_reversed_bounds_are_ordered(self) -> None:
        self.assertLessEqual(
            self.world.options.min_stages_req_for_castle.value,
            self.world.options.max_stages_req_for_castle.value,
        )


class TestGoalExclusion(StickRangerTestBase):
    options = {"goal": "hell_castle", "shuffle_books": 1, "shuffle_enemies": 3}

    def test_non_goal_boss_locations_are_excluded(self) -> None:
        excluded = {
            location.name
            for location in self.multiworld.get_locations(1)
            if location.progress_type is LocationProgressType.EXCLUDED
        }
        self.assertIn("Volcano: Exit", excluded)
        self.assertIn("Mountaintop: Exit", excluded)
        self.assertNotIn("Hell Castle: Exit", excluded)


class TestGoalAllExcludesNothing(StickRangerTestBase):
    options = {"goal": "all", "shuffle_books": 1, "shuffle_enemies": 3}

    def test_nothing_excluded(self) -> None:
        excluded = [
            location.name
            for location in self.multiworld.get_locations(1)
            if location.progress_type is LocationProgressType.EXCLUDED
        ]
        self.assertEqual(excluded, [])

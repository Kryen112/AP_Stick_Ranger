"""The access rules, and the slot_data the client gates its map colouring on."""

from __future__ import annotations

from BaseClasses import LocationProgressType

from ..constants import CLASS_REQ_OPTIONS, ROLLED_OPTIONS
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
                state = self.state_with(
                    *[name for name in every_unlock + every_class if name != held_back]
                )
                region = held_back.removeprefix("Unlock ")
                self.assertFalse(
                    self.can_reach(region, state),
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

    def test_each_boss_waits_for_the_previous_one(self) -> None:
        for index, missing in enumerate(BOSS_CHAIN):
            with self.subTest(missing=missing):
                state = self.state_with(
                    *[f"Unlock {name}" for name in BOSS_CHAIN if name != missing]
                )
                for blocked in BOSS_CHAIN[index:]:
                    self.assertFalse(
                        self.can_reach(blocked, state),
                        f"{blocked} opened without Unlock {missing}",
                    )
                for open_stage in BOSS_CHAIN[:index]:
                    self.assertTrue(
                        self.can_reach(open_stage, state),
                        f"{open_stage} should not care about Unlock {missing}",
                    )

    def test_boss_rush_stages_wait_for_hell_castle(self) -> None:
        for boss_rush in ("Volcano", "Mountaintop"):
            with self.subTest(stage=boss_rush):
                whole_chain = [f"Unlock {name}" for name in BOSS_CHAIN]
                self.assertTrue(
                    self.can_reach(boss_rush, self.state_with(*whole_chain, f"Unlock {boss_rush}"))
                )
                self.assertFalse(
                    self.can_reach(boss_rush, self.state_with(*whole_chain)),
                    f"{boss_rush} opened without its own unlock",
                )
                self.assertFalse(
                    self.can_reach(
                        boss_rush, self.state_with(*whole_chain[:-1], f"Unlock {boss_rush}")
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
        grassland = unlocks_by_region["Grassland"]
        for held in range(5):
            state = self.state_with("Unlock Castle", *grassland[:held])
            self.assertFalse(
                self.can_reach("Castle", state),
                f"Castle opened on {held} Grassland unlocks, needs 5",
            )
        self.assertTrue(
            self.can_reach("Castle", self.state_with("Unlock Castle", *grassland[:5]))
        )

    def test_other_regions_do_not_count(self) -> None:
        state = self.state_with(
            "Unlock Castle", *unlocks_by_region["Sea"], *unlocks_by_region["Hell"]
        )
        self.assertFalse(self.can_reach("Castle", state))


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
        castle = ["Unlock Castle"]
        self.assertFalse(
            self.can_reach("Castle", self.state_with(*castle)),
            "one class should not satisfy three",
        )
        self.assertFalse(
            self.can_reach("Castle", self.state_with(*castle, "Unlock Sniper Class")),
            "two classes should not satisfy three",
        )
        self.assertTrue(
            self.can_reach(
                "Castle", self.state_with(*castle, "Unlock Sniper Class", "Unlock Angel Class")
            ),
            "start + 2 unlocks is 3",
        )


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


class TestTrackerPassthrough(StickRangerTestBase):
    """
    Universal Tracker rebuilds the world from the yaml, so anything decided
    during generation has to come back from slot_data or the tracker disagrees
    with the seed about what is in logic.
    """

    options = {
        "ranger_class_randomizer": 1,
        "min_stages_req_for_castle": 0,
        "max_stages_req_for_castle": 17,
    }

    def test_rolled_values_are_restored_not_rerolled(self) -> None:
        world = self.multiworld.worlds[self.player]
        slot_data = world.fill_slot_data()

        # What UT sends back is exactly what interpret_slot_data returns.
        self.assertEqual(world.interpret_slot_data(slot_data), slot_data)

        # Pretend to be UT: hand the seed's own numbers to a fresh generation
        # and check nothing gets rolled over the top of them.
        pretend = {name: 3 for name in ROLLED_OPTIONS}
        self.multiworld.re_gen_passthrough = {"Stick Ranger": pretend}
        try:
            world.generate_early()
            for name in ROLLED_OPTIONS:
                self.assertEqual(
                    getattr(world.options, name).value,
                    3,
                    f"{name} was re-rolled instead of restored",
                )
        finally:
            del self.multiworld.re_gen_passthrough

    def test_every_rolled_option_is_in_slot_data(self) -> None:
        slot_data = self.multiworld.worlds[self.player].fill_slot_data()
        for name in ROLLED_OPTIONS:
            self.assertIn(name, slot_data, f"{name} is decided at generation but never shipped")

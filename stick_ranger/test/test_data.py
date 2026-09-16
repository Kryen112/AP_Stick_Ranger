"""Integrity of the item and location tables, and of the contract the web client
relies on: item code minus 11000 is the stage id the game uses."""

from __future__ import annotations

from BaseClasses import ItemClassification

from ..constants import GOAL_LOCATIONS, GOAL_OPTIONS_MAP, RANGER_CLASSES, STARTER_UNLOCK_CHOICES
from ..items import classes, filler, item_list, item_table, stages, traps, unlocks_by_region
from ..locations import books_table, enemies_table, location_name_to_id, stages_table
from ..regions import regions
from . import StickRangerTestBase

STAGE_ITEM_OFFSET = 11000

# The stage ids the client counts per region, mirrored from LOGIC_REGION_STAGES
# in game.js. Keeping this list here is the point: if either side drifts, one of
# these repos fails its own tests instead of the map quietly telling players a
# stage is in logic when Archipelago disagrees.
CLIENT_LOGIC_REGION_STAGES: dict[str, list[int]] = {
    "Grassland": [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "Sea": [21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33],
    "Desert": [34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46],
    "Ice": [48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62],
    "Hell": [64, 65, 66, 67, 68, 69, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87],
}


class TestData(StickRangerTestBase):
    run_default_tests = False

    def test_location_names_are_unique(self) -> None:
        seen: set[str] = set()
        for table in (stages_table, books_table, enemies_table):
            for entry in table.values():
                self.assertNotIn(entry["name"], seen, f"duplicate location: {entry['name']}")
                seen.add(entry["name"])
        self.assertEqual(seen, set(location_name_to_id))

    def test_location_ids_are_unique(self) -> None:
        ids = [*stages_table, *books_table, *enemies_table]
        self.assertEqual(len(ids), len(set(ids)), "duplicate location id")

    def test_no_item_name_is_used_twice(self) -> None:
        """
        item_table is keyed by name, so a repeated name silently drops every
        entry but the last -- those items can then never be created or sent.
        Checking item_table itself cannot catch this: it has already collapsed.
        """
        names = [item.item_name for item in item_list]
        duplicated = {name for name in names if names.count(name) > 1}
        self.assertEqual(duplicated, set(), "these item names collapse in item_table")
        self.assertEqual(len(item_list), len(item_table))

    def test_item_codes_are_unique_and_positive(self) -> None:
        codes: set[int] = set()
        for item in item_table.values():
            self.assertGreater(item.code, 0, f"{item.item_name} has a non-positive code")
            self.assertNotIn(item.code, codes, f"duplicate item code: {item.code}")
            codes.add(item.code)

    def test_every_location_region_exists(self) -> None:
        for table in (stages_table, books_table, enemies_table):
            for entry in table.values():
                self.assertIn(entry["region"], regions, f"{entry['name']} has no region")

    def test_every_region_is_reachable_by_an_unlock(self) -> None:
        """Every region except Opening Street needs an item that opens it."""
        unlock_names = {stage.item_name for stage in stages}
        for region in regions:
            if region == "Opening Street":
                continue
            self.assertIn(f"Unlock {region}", unlock_names)

    def test_starter_choices_and_class_items_exist(self) -> None:
        for name in STARTER_UNLOCK_CHOICES:
            self.assertIn(name, item_table)
        self.assertEqual(
            {f"Unlock {name} Class" for name in RANGER_CLASSES},
            {ranger_class.item_name for ranger_class in classes},
        )

    def test_goal_locations_exist(self) -> None:
        for goal, names in GOAL_LOCATIONS.items():
            self.assertIn(f"{goal}: Exit", names)
            for name in names:
                self.assertIn(name, location_name_to_id, f"{goal} names a missing location")
        for goals in GOAL_OPTIONS_MAP.values():
            for goal in goals:
                self.assertIn(goal, GOAL_LOCATIONS)

    def test_classifications(self) -> None:
        for item in filler:
            self.assertIs(item.classification, ItemClassification.filler)
        for trap in traps:
            self.assertIs(trap.classification, ItemClassification.trap)
            self.assertGreater(trap.weight, 0)
        for ranger_class in classes:
            self.assertIs(ranger_class.classification, ItemClassification.progression)

    def test_region_unlock_counts_match_the_client(self) -> None:
        """
        The per-region unlock lists are the denominators of the 'stages required
        for <boss>' options, and the client counts exactly the same stages.
        """
        for region, expected_ids in CLIENT_LOGIC_REGION_STAGES.items():
            stage_ids = sorted(
                item_table[name].code - STAGE_ITEM_OFFSET for name in unlocks_by_region[region]
            )
            self.assertEqual(
                stage_ids,
                expected_ids,
                f"{region} unlocks drifted from the client's LOGIC_REGION_STAGES",
            )

    def test_boss_stages_do_not_count_towards_themselves(self) -> None:
        boss_ids = {
            item_table[name].code - STAGE_ITEM_OFFSET for name in unlocks_by_region["Boss"]
        }
        counted = {i for ids in CLIENT_LOGIC_REGION_STAGES.values() for i in ids}
        self.assertEqual(boss_ids & counted, set())

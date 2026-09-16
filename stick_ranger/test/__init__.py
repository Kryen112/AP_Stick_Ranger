from __future__ import annotations

from test.bases import WorldTestBase


class StickRangerTestBase(WorldTestBase):
    game = "Stick Ranger"

    def collect_items(self, *item_names: str) -> None:
        """
        Collect items by name without going through the item pool.

        collect_by_name only finds items still in the pool, and one Grassland or
        Hill Country unlock is always placed locked on an Opening Street check --
        so a test that happens to name that one silently collects nothing and
        fails on a seed it has nothing to do with.
        """
        for item_name in item_names:
            self.collect(self.world.create_item(item_name))

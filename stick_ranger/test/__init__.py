from __future__ import annotations

from BaseClasses import CollectionState
from test.bases import WorldTestBase


class StickRangerTestBase(WorldTestBase):
    game = "Stick Ranger"

    def state_with(self, *item_names: str) -> CollectionState:
        """
        A state holding exactly these items and nothing else.

        The shared multiworld.state is not usable for counting rules here.
        collect() sweeps, and one Grassland or Hill Country unlock is always
        placed locked on an Opening Street check, so the sweep hands the state a
        region unlock the test never asked for -- which shifts every "needs N
        stages" assertion by one on the seeds where that unlock is not one the
        test was going to collect anyway.
        """
        state = CollectionState(self.multiworld)
        for item_name in item_names:
            state.collect(self.world.create_item(item_name), prevent_sweep=True)
        return state

    def can_reach(self, region_name: str, state: CollectionState) -> bool:
        return self.multiworld.get_region(region_name, self.player).can_reach(state)

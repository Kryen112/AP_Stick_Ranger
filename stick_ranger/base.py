"""The location types every table shares.

They live apart from locations.py so shop.py can build its table without
importing the module that in turn collects every table, which used to force a
late import at the bottom of locations.py.
"""

from __future__ import annotations

from typing import TypedDict

from BaseClasses import Location


class SRLocation(Location):
    game: str = "Stick Ranger"


class LocationDict(TypedDict, total=False):
    name: str
    region: str

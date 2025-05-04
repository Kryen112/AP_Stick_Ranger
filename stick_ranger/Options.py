from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions

class GoldMultiplier(Choice):
    """Multiplies the gold dropped by enemies."""
    display_name = "Gold Multiplier"
    option_1x = 1
    option_2x = 2
    option_5x = 5
    option_10x = 10
    default = 1

class XPMultiplier(Choice):
    """Multiplies the XP gained per enemy killed."""
    display_name = "XP Multiplier"
    option_1x = 1
    option_2x = 2
    option_5x = 5
    option_10x = 10
    default = 1

class DropMultiplier(Choice):
    """Multiplies the chance of enemies dropping an item."""
    display_name = "Drop Multiplier"
    option_1x = 1
    option_2x = 2
    option_5x = 5
    option_10x = 10
    default = 1

@dataclass
class SROptions(PerGameCommonOptions):
    gold_multiplier: GoldMultiplier
    xp_multiplier: XPMultiplier
    drop_multiplier: DropMultiplier

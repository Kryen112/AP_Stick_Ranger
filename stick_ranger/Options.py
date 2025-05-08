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

class BookCostRandomizer(Choice):
    """
    Randomizes the costs of Books.
    vanilla:                         Costs are vanilla (1000*stage number).
    option_random_balanced:          Costs are randomized, but still balanced.
    option_random_extreme:           Costs can range between 1-99999.
    option_random_extreme_expensive: Costs can range between 1-999999. (Not recommended)
    """
    display_name = "Book Cost Randomizer"
    option_vanilla = 0
    option_random_balanced = 1
    option_random_extreme = 2
    option_random_extreme_expensive = 3
    default = 0

@dataclass
class SROptions(PerGameCommonOptions):
    gold_multiplier: GoldMultiplier
    xp_multiplier: XPMultiplier
    drop_multiplier: DropMultiplier
    randomize_book_costs: BookCostRandomizer

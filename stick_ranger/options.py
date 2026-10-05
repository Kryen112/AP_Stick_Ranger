from __future__ import annotations

from dataclasses import dataclass

from Options import (
    Choice,
    DeathLink,
    DefaultOnToggle,
    OptionGroup,
    PerGameCommonOptions,
    Range,
    Toggle,
    Visibility,
)


class Goal(Choice):
    """
    Pick a Goal to finish the game.
    Hell Castle is the usual finish of the game, being the last stage to beat.
    Volcano and Mountaintop are boss rush stages and are therefore regarded has more difficult stages than Hell Castle.
    """

    display_name = "Goal"
    option_hell_castle = 0
    option_volcano = 1
    option_mountaintop = 2
    option_hell_castle_and_volcano = 3
    option_hell_castle_and_mountaintop = 4
    option_volcano_and_mountaintop = 5
    option_all = 6
    default = 0


class RangerClassRandomizer(Toggle):
    """
    When enabled, start with the Class selected in Class Selector, and unlock other Classes via checks.
    This also starts you off with the Forget Tree, to switch Classes, and Forget is free.
    """

    display_name = "Class Randomizer"


class RangerClassSelector(Choice):
    """
    Selects the Class you start with when Class Randomizer is enabled.
    """

    # Unusually for a Choice these options are strings, not ints: the value goes
    # straight into slot_data and the web client matches it against its class
    # name table. from_any resolves the "random" default to a real class.
    display_name = "Class Selector"
    option_boxer = "Boxer"
    option_gladiator = "Gladiator"
    option_sniper = "Sniper"
    option_magician = "Magician"
    option_priest = "Priest"
    option_gunner = "Gunner"
    option_whipper = "Whipper"
    option_angel = "Angel"
    default = "random"


class CastleClassUnlocks(Range):
    """
    Number of Ranger Classes you must have before entering the Castle stage.
    Your starting class counts towards this, so 1 means "no extra classes needed".
    Ignored unless Class Randomizer is enabled, and raised to match an earlier
    boss stage that asks for more.
    """

    display_name = "Classes required for Castle"
    range_start = 0
    range_end = 8
    default = 2


class SubmarineShrineClassUnlocks(Range):
    """
    Number of Ranger Classes you must have before entering the Submarine Shrine stage.
    Your starting class counts towards this, so 1 means "no extra classes needed".
    Ignored unless Class Randomizer is enabled, and raised to match an earlier
    boss stage that asks for more.
    """

    display_name = "Classes required for Submarine Shrine"
    range_start = 0
    range_end = 8
    default = 3


class PyramidClassUnlocks(Range):
    """
    Number of Ranger Classes you must have before entering the Pyramid stage.
    Your starting class counts towards this, so 1 means "no extra classes needed".
    Ignored unless Class Randomizer is enabled, and raised to match an earlier
    boss stage that asks for more.
    """

    display_name = "Classes required for Pyramid"
    range_start = 0
    range_end = 8
    default = 4


class IceCastleClassUnlocks(Range):
    """
    Number of Ranger Classes you must have before entering the Ice Castle stage.
    Your starting class counts towards this, so 1 means "no extra classes needed".
    Ignored unless Class Randomizer is enabled, and raised to match an earlier
    boss stage that asks for more.
    """

    display_name = "Classes required for Ice Castle"
    range_start = 0
    range_end = 8
    default = 5


class HellCastleClassUnlocks(Range):
    """
    Number of Ranger Classes you must have before entering the Hell Castle stage.
    Your starting class counts towards this, so 1 means "no extra classes needed".
    Ignored unless Class Randomizer is enabled, and raised to match an earlier
    boss stage that asks for more.
    """

    display_name = "Classes required for Hell Castle"
    range_start = 0
    range_end = 8
    default = 6


class CastleMinimumStagesUnlocks(Range):
    """
    Minimum number of pre-Castle stages you must unlock before entering the Castle stage.
    Pre-Castle stages are: Grassland 1-7, Lake, Hill Country 1-3, Forest 1&2, Cavern 1-3 and Castle Gate.
    """

    display_name = "Minimum number of required pre-Castle stages"
    range_start = 0
    range_end = 17
    default = 6


class CastleMaximumStagesUnlocks(Range):
    """
    Maximum number of pre-Castle stages you must unlock before entering the Castle stage.
    Pre-Castle stages are: Grassland 1-7, Lake, Hill Country 1-3, Forest 1&2, Cavern 1-3 and Castle Gate.
    """

    display_name = "Maximum number of required pre-Castle stages"
    range_start = 0
    range_end = 17
    default = 10


class StagesReqForCastle(Range):
    """
    Actual number of required pre-Castle stages to beat.
    Only used for rules and tracking.
    """

    display_name = "Actual number of required pre-Castle stages"
    visibility = Visibility.none
    range_start = 0
    range_end = 17
    default = 6


class SubmarineShrineMinimumStagesUnlocks(Range):
    """
    Minimum number of pre-Submarine Shrine stages you must unlock before entering the Submarine Shrine stage.
    Pre-Submarine Shrine stages are: Seaside 1-4, Submarine 1-4, Mist Grove 1-3 and ???.
    """

    display_name = "Minimum number of required pre-Submarine Shrine stages"
    range_start = 0
    range_end = 12
    default = 4


class SubmarineShrineMaximumStagesUnlocks(Range):
    """
    Maximum number of pre-Submarine Shrine stages you must unlock before entering the Submarine Shrine stage.
    Pre-Submarine Shrine stages are: Seaside 1-4, Submarine 1-4, Mist Grove 1-3 and ???.
    """

    display_name = "Maximum number of required pre-Submarine Shrine stages"
    range_start = 0
    range_end = 12
    default = 7


class StagesReqForSubmarineShrine(Range):
    """
    Actual number of required pre-Submarine Shrine stages to beat.
    Only used for rules and tracking.
    """

    display_name = "Actual number of required pre-Submarine Shrine stages"
    visibility = Visibility.none
    range_start = 0
    range_end = 12
    default = 4


class PyramidMinimumStagesUnlocks(Range):
    """
    Minimum number of pre-Pyramid stages you must unlock before entering the Pyramid stage.
    Pre-Pyramid stages are: Desert 1-8, Oasis and Beach 1-3.
    """

    display_name = "Minimum number of required pre-Pyramid stages"
    range_start = 0
    range_end = 12
    default = 4


class PyramidMaximumStagesUnlocks(Range):
    """
    Maximum number of pre-Pyramid stages you must unlock before entering the Pyramid stage.
    Pre-Pyramid stages are: Desert 1-8, Oasis and Beach 1-3.
    """

    display_name = "Maximum number of required pre-Pyramid stages"
    range_start = 0
    range_end = 12
    default = 7


class StagesReqForPyramid(Range):
    """
    Actual number of required pre-Pyramid stages to beat.
    Only used for rules and tracking.
    """

    display_name = "Actual number of required pre-Pyramid stages"
    visibility = Visibility.none
    range_start = 0
    range_end = 12
    default = 4


class IceCastleMinimumStagesUnlocks(Range):
    """
    Minimum number of pre-Ice Castle stages you must unlock before entering the Ice Castle stage.
    Pre-Ice Castle stages are: Cavern 4-6, Snowfield 1-8, Mountain 1&2 and Frozen Lake.
    """

    display_name = "Minimum number of required pre-Ice Castle stages"
    range_start = 0
    range_end = 14
    default = 5


class IceCastleMaximumStagesUnlocks(Range):
    """
    Maximum number of pre-Ice Castle stages you must unlock before entering the Ice Castle stage.
    Pre-Ice Castle stages are: Cavern 4-6, Snowfield 1-8, Mountain 1&2 and Frozen Lake.
    """

    display_name = "Maximum number of required pre-Ice Castle stages"
    range_start = 0
    range_end = 14
    default = 8


class StagesReqForIceCastle(Range):
    """
    Actual number of required pre-Ice Castle stages to beat.
    Only used for rules and tracking.
    """

    display_name = "Actual number of required pre-Ice Castle stages"
    visibility = Visibility.none
    range_start = 0
    range_end = 14
    default = 5


class HellCastleMinimumStagesUnlocks(Range):
    """
    Minimum number of pre-Hell Castle stages you must unlock before entering the Hell Castle stage.
    Pre-Hell Castle stages are: Snowfield 9, Beach 4, Forest 3-6, !!!, Hell 1-8,
    Inferno 1-3, Blood Lake, Cavern 7&8 and Hell Gate.
    """

    display_name = "Minimum number of required pre-Hell Castle stages"
    range_start = 0
    range_end = 22
    default = 7


class HellCastleMaximumStagesUnlocks(Range):
    """
    Maximum number of pre-Hell Castle stages you must unlock before entering the Hell Castle stage.
    Pre-Hell Castle stages are: Snowfield 9, Beach 4, Forest 3-6, !!!, Hell 1-8,
    Inferno 1-3, Blood Lake, Cavern 7&8 and Hell Gate.
    """

    display_name = "Maximum number of required pre-Hell Castle stages"
    range_start = 0
    range_end = 22
    default = 12


class StagesReqForHellCastle(Range):
    """
    Actual number of required pre-Hell Castle stages to beat.
    Only used for rules and tracking.
    """

    display_name = "Actual number of required pre-HellCastle stages"
    visibility = Visibility.none
    range_start = 0
    range_end = 22
    default = 7


class ShuffleBooks(DefaultOnToggle):
    """
    Controls whether buying Books are checks.
    Either Shuffle Books or Shuffle Enemies needs to be turned on.
    """

    display_name = "Shuffle Books"


class ShuffleEnemies(Choice):
    """
    Controls whether enemies drop a check.
    Either Shuffle Enemies or Shuffle Books needs to be turned on.

    common enemies: Every non-boss enemy has a 5% chance to drop.
    boss enemies:   Every boss enemy has a 25% chance to drop.
    both:           Both settings are on.
    """

    display_name = "Shuffle Enemies"
    option_common_enemies = 1
    option_boss_enemies = 2
    option_both = 3
    option_off = 0
    default = 0


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


class ShopHints(Choice):
    """
    What the item shop and the Book shop tell you, and the room, about what
    they sell.

    off:            a shop item that is still a check reads "AP Item" and shows
                    only its price; nothing is hinted.
    important_only: you see everything; the room is only sent hints for
                    progression and traps, so a 462-item shop does not bury
                    everyone else's hints.
    all:            you see everything and every item is hinted to the room.
    """

    display_name = "Shop Hints"
    option_off = 0
    option_important_only = 1
    option_all = 2
    default = 2

    @classmethod
    def from_text(cls, text: str) -> Choice:
        # This was a toggle until 1.8.12, so older yamls say true or false.
        lowered = text.lower()
        if lowered in {"on", "true", "yes", "enabled"}:
            return cls(cls.option_all)
        if lowered in {"off", "false", "no", "disabled"}:
            return cls(cls.option_off)
        return super().from_text(text)


class TrapDisguise(Toggle):
    """
    When enabled, a trap waiting in a shop or a book wears the name of some
    other item in the room, misspelled: "Unlock Laek", "Progressive Eisland
    Shoppe", "Mothwing Cloack".

    It reads as a real item at a glance and gives itself away only if you look
    properly, in the spirit of Ocarina of Time's ice traps. While it is on the
    shops never send a hint for a trap, since the hint would carry its real
    name; that quiet is itself a small tell, but a smaller one. Anyone else
    scouting the location by other means still sees the trap for what it is.
    """

    display_name = "Trap Disguise"


class BookCostRandomizer(Choice):
    """
    Randomizes the costs of Books.

    vanilla:                  Costs are vanilla (1000*stage number).
    random_balanced:          Costs are randomized, but still balanced.
    random_extreme:           Costs can range between 1-99999.
    random_extreme_expensive: Costs can range between 1-999999. (Not recommended)
    vanilla_tenth:            Costs are vanilla divided by 10.
    """

    display_name = "Book Cost Randomizer"
    option_vanilla = 0
    option_random_balanced = 1
    option_random_extreme = 2
    option_random_extreme_expensive = 3
    option_vanilla_tenth = 4
    default = 0


class TrapPercentage(Range):
    """
    What share of the filler items are Traps, as a percentage.

    The share is of the items left once every stage and class unlock is placed,
    so at 100 every non-progression check you find is a Trap and Archipelago
    never hands you a weapon or a compo.
    """

    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0

    @classmethod
    def from_text(cls, text: str) -> Range:
        # 1.8 yamls wrote `traps: none`; their other values were the numbers
        # themselves. A bare number used to be read as the position in a list
        # of choices, which is how `traps: 5` once meant every filler a trap.
        if text.lower() == "none":
            return cls(0)
        return super().from_text(text)


class RingLink(Toggle):
    """
    When enabled, your gold is linked to every other Ring Link player's rings.

    Gold you gain sends rings to the room; rings you receive become gold. It
    works in both directions, so spending sends a negative.
    """

    display_name = "Ring Link"


class RingLinkRatio(Range):
    """
    How much gold one Ring Link ring is worth, in both directions.

    Stick Ranger's gold is one to two orders of magnitude larger than the ring
    counts games like Sonic deal in -- a single enemy drops up to 9999 -- so
    sending gold unscaled would flood the room. At the default, earning 300 gold
    sends 3 rings and receiving 10 rings pays 1000 gold.
    """

    display_name = "Ring Link Ratio"
    range_start = 1
    range_end = 1000
    default = 100


class RingGold(Range):
    """
    Gold earned every time an Angel throws a ring, with Ring Link on. 0 turns
    it off.

    This is Ring Link's payout: the gold goes out to the room as rings like any
    other gold you earn, so your Angels' rings are what you send. It does
    nothing unless Ring Link is on.

    Angels throw roughly two rings a second each, or seven on a quick ring, so
    four of them at the maximum out-earns every enemy in the game several times
    over. The payout is flat: it ignores the Gold Multiplier and the Gold Medal,
    so the number here is the number you get.
    """

    display_name = "Gold per Thrown Ring"
    range_start = 0
    range_end = 1000
    default = 50


class EnforceLogic(Toggle):
    """
    When enabled, stages that are out of logic cannot be entered at all.

    They still show on the map, greyed out, so you can see what you hold. There
    is no way to override it mid-run, which is the point: the run cannot be
    broken by accident or on purpose.
    """

    display_name = "Enforce Logic"


class ShopChecks(Toggle):
    """
    When enabled, buying each item in a shop for the first time sends a check.

    That is 462 checks, one per item the shops stock, wherever you buy it. The
    shop shows an Archipelago logo until the check has been collected, and the
    normal item afterwards.
    """

    display_name = "Shop Checks"


class ProgressiveShop(Toggle):
    """
    When enabled, each town's shop stock is unlocked by its own Progressive
    Shop items instead of by completing stages.

    Every shop has its own track, so opening Island's stock does not open
    Town's: 32 Progressive Town Shop, 15 Village, 1 Resort and 33 Island. Town
    keeps its first row stocked because that is where you start; Village,
    Resort and Island hold nothing at all until their own first item arrives,
    and say so.

    In the base game only Town's stock grows with the stages you beat; Village,
    Resort and Island sell everything the moment you arrive. So this option
    replaces Town's gating and adds gating to the other three.

    Does nothing unless Shop Checks is on.
    """

    display_name = "Progressive Shop"


class EnforceShopLogic(Toggle):
    """
    When enabled, a shop item that Archipelago does not consider reachable yet
    cannot be bought. It is greyed out until the world has opened far enough.

    This is the shop's half of Enforce Logic. Without it the shop still sells
    anything it has stocked -- logic simply does not count on you buying it.

    Does nothing unless Shop Checks is on.
    """

    display_name = "Enforce Shop Logic"


class FreeRespec(Toggle):
    """
    When enabled, respeccing at the Forget Tree is always free.

    Class Randomizer already makes it free, since it hands you the Forget Tree
    to swap class with. This makes it free without that option too, instead of
    costing 1000 gold per spent skill point.
    """

    display_name = "Free Respec"


class RemoveNullCompo(DefaultOnToggle):
    """When enabled, buying weapons from the shop removes the 'cross' compo from the second compo slot"""

    display_name = "Remove Null Compo"


class RemovableCompos(Toggle):
    """
    When enabled, a compo already fitted to a weapon can be taken back out by
    clicking its slot with an empty hand. It returns to your cursor intact.

    In the base game a compo is in for good once fitted, so a good one sunk into
    a starter weapon is gone. This does not touch the cross that blocks a
    store-bought slot -- Remove Null Compo covers that one.
    """

    display_name = "Removable Compos"


# The 1.8 yaml keys of two options that have since changed shape. Hidden, so
# nothing offers them, but a yaml that still carries them is read instead of
# being warned about and ignored: Archipelago only logs an unknown key, and the
# seed would have generated with no traps and every shop item hinted.
# generate_early folds each into the option that replaced it.
class LegacyTraps(TrapPercentage):
    """
    The old name of Trap Percentage. `traps: 20` meant twenty percent and
    `traps: none` meant none, and both still do.
    """

    display_name = "Traps (old name of Trap Percentage)"
    visibility = Visibility.none


class LegacyImportantHintsOnly(Toggle):
    """The old toggle that is now the `important_only` value of Shop Hints."""

    display_name = "Important Hints Only (old form of Shop Hints)"
    visibility = Visibility.none


@dataclass
class SROptions(PerGameCommonOptions):
    # Field order is the order of the yaml template, and SR_OPTION_GROUPS below
    # lays the options page out the same way. The StagesReqFor* fields are
    # hidden: they hold what generation rolled between each min and max.
    goal: Goal
    # Checks
    shuffle_books: ShuffleBooks
    shuffle_enemies: ShuffleEnemies
    shop_checks: ShopChecks
    progressive_shop: ProgressiveShop
    randomize_book_costs: BookCostRandomizer
    # Ranger classes
    ranger_class_randomizer: RangerClassRandomizer
    ranger_class_selected: RangerClassSelector
    classes_req_for_castle: CastleClassUnlocks
    classes_req_for_submarine_shrine: SubmarineShrineClassUnlocks
    classes_req_for_pyramid: PyramidClassUnlocks
    classes_req_for_ice_castle: IceCastleClassUnlocks
    classes_req_for_hell_castle: HellCastleClassUnlocks
    # Boss stage requirements
    min_stages_req_for_castle: CastleMinimumStagesUnlocks
    max_stages_req_for_castle: CastleMaximumStagesUnlocks
    stages_req_for_castle: StagesReqForCastle
    min_stages_req_for_submarine_shrine: SubmarineShrineMinimumStagesUnlocks
    max_stages_req_for_submarine_shrine: SubmarineShrineMaximumStagesUnlocks
    stages_req_for_submarine_shrine: StagesReqForSubmarineShrine
    min_stages_req_for_pyramid: PyramidMinimumStagesUnlocks
    max_stages_req_for_pyramid: PyramidMaximumStagesUnlocks
    stages_req_for_pyramid: StagesReqForPyramid
    min_stages_req_for_ice_castle: IceCastleMinimumStagesUnlocks
    max_stages_req_for_ice_castle: IceCastleMaximumStagesUnlocks
    stages_req_for_ice_castle: StagesReqForIceCastle
    min_stages_req_for_hell_castle: HellCastleMinimumStagesUnlocks
    max_stages_req_for_hell_castle: HellCastleMaximumStagesUnlocks
    stages_req_for_hell_castle: StagesReqForHellCastle
    # Logic
    enforce_logic: EnforceLogic
    enforce_shop_logic: EnforceShopLogic
    # Traps and hints
    trap_percentage: TrapPercentage
    trap_disguise: TrapDisguise
    shop_hints: ShopHints
    # Quality of life
    gold_multiplier: GoldMultiplier
    xp_multiplier: XPMultiplier
    drop_multiplier: DropMultiplier
    free_respec: FreeRespec
    remove_null_compo: RemoveNullCompo
    removable_compos: RemovableCompos
    # Links
    ring_link: RingLink
    ring_link_ratio: RingLinkRatio
    ring_gold: RingGold
    death_link: DeathLink
    # 1.8 yaml keys, hidden and folded into the options above; see LegacyTraps.
    traps: LegacyTraps
    important_hints_only: LegacyImportantHintsOnly


# Layout for the WebHost player-options page, in the same order as the yaml
# template follows (the field order of SROptions). Goal stays in Archipelago's
# own default group at the top; the hidden StagesReqFor* options are rolled
# during generation and deliberately left out.
SR_OPTION_GROUPS: list[OptionGroup] = [
    OptionGroup(
        "Checks",
        [ShuffleBooks, ShuffleEnemies, ShopChecks, ProgressiveShop, BookCostRandomizer],
    ),
    OptionGroup(
        "Ranger Classes",
        [
            RangerClassRandomizer,
            RangerClassSelector,
            CastleClassUnlocks,
            SubmarineShrineClassUnlocks,
            PyramidClassUnlocks,
            IceCastleClassUnlocks,
            HellCastleClassUnlocks,
        ],
    ),
    OptionGroup(
        "Boss Stage Requirements",
        [
            CastleMinimumStagesUnlocks,
            CastleMaximumStagesUnlocks,
            SubmarineShrineMinimumStagesUnlocks,
            SubmarineShrineMaximumStagesUnlocks,
            PyramidMinimumStagesUnlocks,
            PyramidMaximumStagesUnlocks,
            IceCastleMinimumStagesUnlocks,
            IceCastleMaximumStagesUnlocks,
            HellCastleMinimumStagesUnlocks,
            HellCastleMaximumStagesUnlocks,
        ],
    ),
    OptionGroup(
        "Logic",
        [EnforceLogic, EnforceShopLogic],
    ),
    OptionGroup(
        "Traps and Hints",
        [TrapPercentage, TrapDisguise, ShopHints],
    ),
    OptionGroup(
        "Quality of Life",
        [GoldMultiplier, XPMultiplier, DropMultiplier, FreeRespec, RemoveNullCompo, RemovableCompos],
    ),
    OptionGroup(
        "Links",
        [RingLink, RingLinkRatio, RingGold, DeathLink],
    ),
]

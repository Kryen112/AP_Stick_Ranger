# Stick Ranger integration for Archipelago

## Table of Contents

1. [Installation](#installation)
2. [AP Integration](#ap-integration)
    - [Goal](#goal)
    - [Locations](#locations)
    - [Items](#items)
    - [Progression](#progression)
    - [Options](#options)
3. [Saving & Persistence](#saving--persistence)
4. [Building the apworld](#building-the-apworld)
5. [Tests](#tests)
6. [Contributing](#contributing)
7. [License](#license)
8. [Contact & Support](#contact--support)
9. [Acknowledgements](#acknowledgements)

---

## Installation

-   Download the APworld for Stick Ranger
-   Put the stick_ranger.apworld in the /custom_worlds folder inside Archipelago
-   Generate a yaml or download the one in here
-   Customize the yaml and put it in the /players folder inside Archipelago
-   Generate a game
-   Connect to and play the game [here](https://kryen112.github.io/)

## AP Integration

### Goal

The goal of the game is to complete the Hell Castle stage.

### Locations

Checks are send when:

-   You complete a stage
-   You buy a book (when book_shuffle is on)
-   When an AP item from an enemy is dropped and picked up (when enemy_shuffle is on)

### Items

You can receive:

-   Stage unlocks
-   Class unlocks (if class_shuffle is enabled)
-   A random item (any weapon/compo)
-   Traps (if enabled)

### Progression

Five boss stages gate the game, each waiting on the one before it:

    Castle -> Submarine Shrine -> Pyramid -> Ice Castle -> Hell Castle

A boss opens once you hold its own stage unlock, enough stage unlocks from the
region in front of it, and enough ranger classes (your starting class counts).
The stages counted per boss are:

| Boss             | Counts             | Out of |
| ---------------- | ------------------ | ------ |
| Castle           | pre-Castle stages  | 17     |
| Submarine Shrine | sea stages         | 12     |
| Pyramid          | desert stages      | 12     |
| Ice Castle       | ice stages         | 14     |
| Hell Castle      | hell stages        | 22     |

Volcano and Mountaintop are boss rush stages sitting behind the Hell Castle gate.

The world map colours each stage dot by the same rules: yellow is in logic,
orange is unlocked but out of logic, dark red means every check there has been
sent, and white is a town. `in_logic()` in the web client mirrors
`stick_ranger/rules.py`, and both repos have a test pinning the region lists so
they cannot drift apart silently.

### Options

-   Book shuffle
-   Class shuffle
-   Amount of classes to have before each boss stage
-   Enemy shuffle
-   Enemy gold drop value multiplier
-   XP gain multiplier
-   Enemy drop multiplier
-   Book shop hints
-   Book cost randomizer
-   Traps
-   DeathLink

## Saving & Persistence

-   **Save state is on Archipelago's DataStorage** 
-   **Key structure**:
    ```
    Stick Ranger:[slotName]:[seed]
    ```
-   Auto-save triggers:
    -   Receiving items
    -   Sending checks
    -   Scouting Book locations (Opening Book shop)

## Building the apworld

Packaging goes through Archipelago's own `Build APWorlds` Launcher component,
which is what writes the `archipelago.json` manifest (required from AP 0.7.0),
drops `__pycache__` and guarantees portable path separators in the archive.

Once, to let Archipelago see the world:

```sh
py -3.12 build_apworld.py --link
```

That links `<Archipelago>/worlds/stick_ranger` at this repo. Point `AP_ROOT` at
your Archipelago source checkout if it is not a sibling of this folder. Then:

```sh
py -3.12 build_apworld.py
```

builds, verifies and installs `stick_ranger.apworld` into `custom_worlds`. Add
`--no-install` to build without copying it anywhere.

## Tests

```sh
py -3.12 scripts/run_world_tests.py
```

runs the world's tests inside the linked Archipelago checkout. CI runs the same
suite plus Archipelago's general world tests on every push.

## Contributing

Feel free to contribute or mod.

## License

This project is licensed under the **[MIT License](LICENSE)**. Feel free to use, modify, and distribute.

## Contact & Support

Please contact inside the Archipelago Discord, inside the Stick Ranger post inside future-game-design, or contact Kryen112 on Discord directly.

## Acknowledgements

-   Please support ha55ii, the original creator of Stick Ranger, by playing his games on [dan-ball](http://dan-ball.jp), including the original Stick Ranger and other web games.
-   Thanks to Dire Storm from the Dan-Ball Discord for making a Vanilla Translation Mod.
-   Thanks to sunsetquesar for teaching me how to run a github.io page.

---

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
4. [Contributing](#contributing)
5. [License](#license)
6. [Contact & Support](#contact--support)
7. [Acknowledgements](#acknowledgements)
8. [Local Web Server Help](#local-web-server-help)

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

Progression is locked into 5 zones:

-   Everything before Castle
-   Everything before Submarine Shrine
-   Everything before Pyramid
-   Everything before Ice Castle
-   Everything after Ice Castle

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

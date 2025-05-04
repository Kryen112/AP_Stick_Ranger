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
4. [Roadmap](#roadmap)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact & Support](#contact--support)
8. [Acknowledgements](#acknowledgements)
9. [Local Web Server Help](#local-web-server-help)

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

The goal of the game is to complete the Hell Castle stage

### Locations

Checks are send when:

-   You complete a stage
-   You buy a book

### Items

You can receive:

-   Stage unlocks
-   A random item (any weapon/compo)

### Progression

Progression is locked into 5 zones:

-   Everything before Castle
-   Everything before Submarine Shrine
-   Everything before Pyramid
-   Everything before Ice Castle
-   Everything after Ice Castle

### Options

-   Enemy gold drop value multiplier
-   XP gain multiplier
-   Enemy drop multiplier

## Saving & Persistence

-   **IndexedDB** store name: `StickRangerAP`
-   **Object store**: `savegames`
-   **Key structure**:
    ```
    [hostname]:[port]:Stick Ranger:[slotName]
    ```
-   Auto-save triggers:
    -   Receiving items
    -   Sending checks

## Roadmap

-   [x] Initial Release
-   [ ] Additional yaml options
-   [ ] DeathLink
-   [ ] Book shop buy item preview
-   [ ] Send commands/chat via chat window
-   [ ] Traps
-   [ ] Enemy/item randomizer

## Contributing

-   Local web server (Running "Archipelago Mod.html") (Need help? See [Local Web Server Help](#local-web-server-help))

Feel free to contribute or mod

## License

This project is licensed under the **[MIT License](LICENSE)**. Feel free to use, modify, and distribute.

## Contact & Support

Please contact inside the Archipelago Discord, inside the Stick Ranger post inside future-game-design, or contact Kryen112 on Discord directly

## Acknowledgements

-   Please support ha55ii, the original creator of Stick Ranger, by playing his games on [dan-ball](http://dan-ball.jp), including the original Stick Ranger and other web games.
-   Thanks to Dire Storm from the Dan-Ball Discord for making a Vanilla Translation Mod
-   Thanks to sunsetquesar for teaching me how to run a github.io page

## Local Web Server Help

For easy setup of a local web server, do the following:

-   Install [Visual Studio Code](https://code.visualstudio.com/)
-   Install the [Live Server](https://marketplace.visualstudio.com/items/?itemName=ritwickdey.LiveServer) extension inside Visual Studio Code
-   Open the "Archipelago Mod" folder inside Visual Studio Code
-   Click ![go_live_image](assets/go_live.png) in the bottom-right of Visual Studio Code
-   A tab on your preferred browser will now open on http://127.0.0.1:5500/Archipelago%20Mod.html, running the game!

---

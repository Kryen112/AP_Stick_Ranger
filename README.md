# Stick Ranger integration for Archipelago

## Table of Contents

1. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
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

## Getting Started

### Prerequisites

List any software or hardware requirements, e.g.:

-   A modern web browser (Chrome, Firefox, Edge...) (Only tested in Firefox)
-   Local web server

### Installation

-   Download the APworld for Stick Ranger
-   Put the stick_ranger.apworld in the /custom_worlds folder inside Archipelago
-   Generate a yaml or download the one in here
-   Customize the yaml and put it in the /players folder inside Archipelago
-   Generate a game
-   Run your local web server (Running "Archipelago Mod.html") (Need help? See [Local Web Server Help](#local-web-server-help))
-   Connect to and play the game (http://127.0.0.1:5500/Archipelago%20Mod.html)

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

At the moment there are no options yet

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

Feel free to contribute or mod

## License

This project is licensed under the **[MIT License](LICENSE)**. Feel free to use, modify, and distribute.

## Contact & Support

Please contact inside the Archipelago Discord, inside the Stick Ranger post inside future-game-design, or contact Kryen112 on Discord directly

## Acknowledgements

-   Thanks to Dire Storm from the Dan-Ball Discord for making a Vanilla Translation Mod

## Local Web Server Help

For easy setup of a local web server, do the following:

-   Install [Visual Studio Code](https://code.visualstudio.com/)
-   Install the [Live Server](https://marketplace.visualstudio.com/items/?itemName=ritwickdey.LiveServer) extension inside Visual Studio Code
-   Open the "Archipelago Mod" folder inside Visual Studio Code
-   Click ![go_live_image](assets/go_live.png) in the bottom-right of Visual Studio Code
-   A tab on your preferred browser will now open on http://127.0.0.1:5500/Archipelago%20Mod.html, running the game!

---

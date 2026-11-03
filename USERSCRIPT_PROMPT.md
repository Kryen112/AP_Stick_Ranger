# Task: rebuild the Stick Ranger Archipelago client as a Tampermonkey userscript for the official dan-ball.jp page

## Repository layout

Paths below are relative to the folder that holds these repos side by side:

- `AP_Stick_Ranger/`: the apworld (this repo, https://github.com/Kryen112/AP_Stick_Ranger)
- `Kryen112.github.io/`: the current web client and hosted game (https://github.com/Kryen112/Kryen112.github.io)
- `AP_Stick_Ranger_Userscript/`: the new userscript project (to be created)

Clone any that are missing next to each other, and pull both existing repos to their latest `main` before starting. The function names, `window.ArchipelagoMod` properties and option names listed below were taken from an older version of both repos (website 1.5.1). Treat them as a starting point and re-derive the real list from the latest code.

## Why this exists

My Stick Ranger Archipelago integration is currently a website (`Kryen112.github.io/`, live at https://kryen112.github.io/) that hosts a full copy of the game: `public/game.js` (and its build copy `docs/game.js`), the game's art in `public/data/`, and the Dan-Ball font `src/dan-ball.otf`. That game.js is ha55ii's code (header: "Copyright (C) 2008 ha55ii ... The games source code use is prohibition."), de-obfuscated and translated by a modder (Dire Storm), with my AP edits mixed in. The Archipelago Discord forbids posting or linking copyrighted material (rule 3). The moderators said a patch that contains no foreign copyrighted material and modifies the game is acceptable. Getting permission from ha55ii is not possible.

So the goal: a userscript that runs on the official Stick Ranger page on dan-ball.jp, leaves the game loading from Dan-Ball's own servers, and adds the Archipelago client on top. The script must ship nothing of ha55ii's.

## Hard rules (copyright)

1. Ship none of ha55ii's code, art, sounds, text or font. No copies of game.js, the GIFs in `public/data/`, or `dan-ball.otf`, not even embedded as data URIs.
2. Hooks must not contain ha55ii's code. Don't paste a modified copy of one of the game's functions into the script, even a "rewritten" one. Prefer thin wrappers: save the original function, replace it with a function that calls the original and reacts to the result or state, or patch game state/data from outside.
3. Preferred order of techniques:
   a. Wrap or replace functions and objects that are reachable from `window` (or another reachable scope).
   b. Read and write game state (inventory, stage flags, classes, gold) directly.
   c. Only if a hook is impossible without it: transform the game's source at load time with minimal find/replace anchors. Before using (c) at all, STOP and ask me, explaining why (a)/(b) can't work for that hook. It may need another check with the moderators.
4. My own assets are fine to embed: the AP icons `public/data/AP.gif`, `AP_grey.gif`, `AP_icon.gif`, `AP_icon_grey.gif` (24x24 and 18x18) were made by me. Embed them as data URIs.

## Sources to study

- `Kryen112.github.io/src/main.js`: my current client, class `APIntegration`, instantiated as `window.ap`. It uses `archipelago.js` (^2.0.4) and covers connect/disconnect UI, DataStorage save/load (key `Stick Ranger:[slotName]:[seed]`), receiving items (`_applyItem`), traps (`_applyTrap`: unequipItems, loseHalfGold, killRanger, freezeRangers, spawnEnemies), DeathLink (`die`), sending checks (`sendLocation`), book scouting/hints when the book shop opens (`scoutBooksOnShopOpen`), randomized book costs (`createRandomizedBookCosts`), stage unlock gating from slot data (`setStagesToWinFromGoal`), and a tick loop (`_tick` / `_doTickWork`) that polls game state. Port its logic. It's my code, so reuse is fine.
- `Kryen112.github.io/index.html`: the current UI around the game (connect form, log, font switch). Rebuild it as an overlay or side panel on the dan-ball page.
- `Kryen112.github.io/public/game.js`: USE AS A MAP ONLY, NEVER COPY FROM IT. Each translated variable/function carries a comment like `// original name: Wc`, which tells you the obfuscated name in the official build. My AP edits inside it all go through `window.ArchipelagoMod` and are the hook points you need to reproduce from outside. Find them with `grep -n "ArchipelagoMod\|AP_Img\|AP_Icon" public/game.js`.
  - Properties the game reads: enemyIdsSent, shuffleEnemies, rangerClassRandomizer, rangerClassesUnlocked, bookHintSpoiler, xpMultiplier, goldMultiplier, dropMultiplier, stagesForCastle/SubmarineShrine/Pyramid/IceCastle/HellCastle, classesForCastle/SubmarineShrine/Pyramid/IceCastle/HellCastle, shuffleBooks, removeNullCompo, randomizedBookCosts, bookCostRandomizer, pendingSave, pendingClassSwapItems, pendingAPItemDrops.
  - Behaviours to reproduce: class selection limited to unlocked classes; AP icons on enemy info and drops (grey once sent); book shop hint text and randomized book costs; null compo removed from the weapon shop; XP/gold/drop multipliers; AP item drops from enemies; stage locking and boss gating.
- `AP_Stick_Ranger/stick_ranger/`: the apworld (`constants.py`, `items.py`, `locations.py`, `options.py`, `rules.py`, `shop.py`, docs). Its item/location IDs and slot data define the protocol. Keep the apworld unchanged unless a change is unavoidable, and if so, tell me first.
- `AP_Stick_Ranger/stick_ranger/client.py`: the Launcher component. It turns an `archipelago://` room link into a `https://kryen112.github.io/` URL with host, port and slot as query parameters for the connect form. Under the userscript it has to open the dan-ball page instead, with the userscript reading those parameters. This is the one apworld change I expect; propose it to me rather than making it unasked.

## First step: verify the official build before writing hooks

1. Find the official English Stick Ranger page on dan-ball.jp (likely https://dan-ball.jp/en/javagame/ranger/) and how it loads the game script.
2. Check whether the official build matches what my mod was built on (the header says "Stick Ranger 18.9 / Patch version 19.11"). Dire Storm's version also changed gameplay/UI (debug option, SP indicators, DPS, greyed book stages, arrow-key scrolling, restored desert haze, anticheat logging, among others). Those changes are NOT in the official build and are out of scope. Don't rebuild them.
3. Work out how reachable the game's functions/state are from a userscript: globals, or a closure/IIFE? Report this to me with a list of every hook point and the technique per hook (3a/3b/3c) BEFORE implementing. If any hook needs 3c, ask me first (rule 3).

## Deliverable

- A new project folder `AP_Stick_Ranger_Userscript/` (git repo) next to the other two, producing one installable `.user.js` with a proper `// ==UserScript==` header (`@match` for the dan-ball Stick Ranger page, `@version`, `@updateURL`/`@downloadURL` later). Recommended build: Vite with vite-plugin-monkey, bundling archipelago.js into the script. Alternatively, a pinned `@require` from cdn.jsdelivr.net.
- Feature parity with the current client for everything that lives on my side (all apworld options: book shuffle, class shuffle, classes/stages needed per boss zone, enemy shuffle, multipliers, book hints, book cost randomizer, traps, DeathLink, DataStorage persistence and resume).
- A README for players: install Tampermonkey, install the script, open the dan-ball page, connect. Credit ha55ii and link to dan-ball.jp.
- Make clear where the save lives. The official game may keep its own save (e.g. localStorage or cookies on dan-ball.jp); make sure the AP state and the game save can't get out of sync, and document how to start a fresh run.

## Out of scope

- Taking the game files down from Kryen112.github.io. I'll handle that separately.
- Gameplay or UI changes beyond what the AP integration needs.

## Working style

- Ask me one design question at a time, always with your recommendation.
- Stay within this scope. Don't expand it without asking.
- Commit only when I ask. Commit author: Kryen112 <Kryen112@hotmail.com>. Commit message is one sentence with semicolon-separated clauses, no body, no AI attribution, no personal names.
- Code comments describe the current state only, never the change history.
- Spell domain terms in full in identifiers (e.g. `submarineShrine`, never `subShrine`).

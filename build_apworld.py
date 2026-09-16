"""Build stick_ranger.apworld and install it into the local Archipelago.

Run from the repo root:
    py -3.12 build_apworld.py

Packaging only, no code generation -- everything under stick_ranger/ is committed
source. The build delegates to Archipelago's own `Build APWorlds` Launcher
component rather than zipping the folder by hand, because that component is the
only thing that produces a *portable* .apworld:

  * it writes the `archipelago.json` manifest into the archive (AP 0.7.0 refuses
    to load an .apworld without one),
  * it honours data/GLOBAL.apignore, so `__pycache__` and other host-specific
    junk never ships,
  * it writes archive entries through `zipfile`, which always normalises to
    forward slashes -- a hand-rolled `Compress-Archive` depends on the host's
    PowerShell version for that, and a backslash entry is unreadable on Linux
    and macOS.

Archipelago has to be able to see the world as `worlds/stick_ranger`. Pass
--link once to create that link (a directory junction on Windows, a symlink
elsewhere) pointing at this repo's stick_ranger/ folder.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
WORLD_DIR = REPO_ROOT / "stick_ranger"
PACKAGE_NAME = "stick_ranger"
APWORLD_GAME_NAME = "Stick Ranger"
APWORLD_FILE = f"{PACKAGE_NAME}.apworld"

# The Archipelago source checkout whose Launcher builds the archive. Default:
# the sibling of this repo, matching the usual Archipelago-play/ layout.
AP_ROOT = Path(os.environ.get("AP_ROOT") or (REPO_ROOT.parent / "Archipelago")).resolve()

# --- LOCAL ONLY, do not commit -------------------------------------------
# Drop the built apworld into each local custom_worlds so the running generator
# and launcher pick up the rebuild. Machine-specific; override with
# SR_APWORLD_INSTALL_DIRS (os.pathsep-separated).
_DEFAULT_INSTALL_DIRS = [Path(r"C:\ProgramData\Archipelago\custom_worlds")]
INSTALL_DIRS = (
    [Path(p) for p in os.environ["SR_APWORLD_INSTALL_DIRS"].split(os.pathsep)]
    if os.environ.get("SR_APWORLD_INSTALL_DIRS")
    else _DEFAULT_INSTALL_DIRS
)
# --- end LOCAL ONLY -------------------------------------------------------


def linked_world_dir() -> Path:
    return AP_ROOT / "worlds" / PACKAGE_NAME


def create_link() -> int:
    """Point <AP_ROOT>/worlds/stick_ranger at this repo's world folder."""
    target = linked_world_dir()
    if target.exists():
        print(f"{target} already exists; remove it first if you want to relink.")
        return 1
    if not (AP_ROOT / "Launcher.py").is_file():
        print(f"ERROR: no Archipelago checkout at {AP_ROOT}; set AP_ROOT.", file=sys.stderr)
        return 1
    if os.name == "nt":
        # A junction needs no elevation; a symlink does unless Developer Mode is on.
        subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(WORLD_DIR)], check=True)
    else:
        target.symlink_to(WORLD_DIR, target_is_directory=True)
    print(f"Linked {target} -> {WORLD_DIR}")
    return 0


def check_link() -> None:
    """Fail early with an actionable message if AP cannot see the world."""
    if not (AP_ROOT / "Launcher.py").is_file():
        raise FileNotFoundError(
            f"no Archipelago checkout at {AP_ROOT}. Set AP_ROOT to your Archipelago "
            f"source folder, or place it next to this repo."
        )
    target = linked_world_dir()
    if not (target / "__init__.py").is_file():
        raise FileNotFoundError(
            f"Archipelago cannot see the world at {target}. Run:\n"
            f"    py -3.12 build_apworld.py --link"
        )


def build_apworld_zip() -> Path:
    """Invoke AP's `Build APWorlds` component and return the archive it wrote."""
    cmd = [sys.executable, "Launcher.py", "Build APWorlds", APWORLD_GAME_NAME]
    result = subprocess.run(cmd, cwd=AP_ROOT, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"'Build APWorlds' exited {result.returncode}; no .apworld produced.")
    zip_path = AP_ROOT / "build" / "apworlds" / APWORLD_FILE
    if not zip_path.is_file():
        raise RuntimeError(f"Launcher reported success but {zip_path} is missing.")
    return zip_path


def verify(zip_path: Path) -> None:
    """Refuse to ship an archive that AP 0.7 would reject or that unpacks wrong
    off Windows."""
    import json
    import zipfile

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        manifest_path = f"{PACKAGE_NAME}/archipelago.json"
        if manifest_path not in names:
            raise RuntimeError(f"{zip_path} has no {manifest_path}")
        backslashed = [name for name in names if chr(92) in name]
        if backslashed:
            raise RuntimeError(f"{zip_path} has non-portable entry names: {backslashed[:3]}")
        cached = [name for name in names if "__pycache__" in name]
        if cached:
            raise RuntimeError(f"{zip_path} ships __pycache__: {cached[:3]}")
        manifest = json.loads(zf.read(manifest_path))

    if manifest.get("game") != APWORLD_GAME_NAME:
        raise RuntimeError(f"manifest game is {manifest.get('game')!r}, expected {APWORLD_GAME_NAME!r}")
    print(
        f"Verified {len(names)} entries, world_version {manifest.get('world_version')}, "
        f"container version {manifest.get('version')}"
    )


# --- LOCAL ONLY, do not commit -------------------------------------------
def install(zip_path: Path) -> None:
    """Copy the built apworld into each local custom_worlds dir. Skips missing dirs."""
    for dest_dir in INSTALL_DIRS:
        if not dest_dir.is_dir():
            print(f"  skipped install (no such dir): {dest_dir}")
            continue
        dest = dest_dir / zip_path.name
        shutil.copy2(zip_path, dest)
        print(f"  installed -> {dest}")
# --- end LOCAL ONLY -------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--link",
        action="store_true",
        help="create <AP_ROOT>/worlds/stick_ranger pointing at this repo, then exit",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="build and verify only; do not copy into custom_worlds",
    )
    args = parser.parse_args()

    if args.link:
        return create_link()

    check_link()
    zip_path = build_apworld_zip()
    verify(zip_path)
    print(f"Built {zip_path} ({zip_path.stat().st_size // 1024} KB)")

    # Keep a copy next to the sources; .gitignore'd, handy for uploading a release.
    local_copy = REPO_ROOT / APWORLD_FILE
    shutil.copy2(zip_path, local_copy)
    print(f"  copied -> {local_copy}")

    if not args.no_install:
        install(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

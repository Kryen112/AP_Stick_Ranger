"""Run the world's tests inside the linked Archipelago checkout.

The tests subclass test.bases.WorldTestBase and exercise fill, so they only run
from within an Archipelago tree. If none is linked this exits 0 with a note
rather than failing the commit -- a checkout is a local dev convenience, not a
requirement for editing the world.

    py -3.12 scripts/run_world_tests.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AP_ROOT = Path(os.environ.get("AP_ROOT") or (REPO_ROOT.parent / "Archipelago")).resolve()
LINKED_WORLD = AP_ROOT / "worlds" / "stick_ranger"


def main() -> int:
    if not (LINKED_WORLD / "__init__.py").is_file():
        print(
            f"No Archipelago checkout with the world linked at {LINKED_WORLD}; "
            f"skipping tests. Link it with: py -3.12 build_apworld.py --link"
        )
        return 0
    return subprocess.run(
        [sys.executable, "-m", "pytest", "worlds/stick_ranger/test", "-q"],
        cwd=AP_ROOT,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())

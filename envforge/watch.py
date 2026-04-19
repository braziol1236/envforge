"""Watch for environment variable changes and auto-snapshot."""

import os
import time
from typing import Optional
from envforge.snapshot import save_snapshot, load_snapshot
from envforge.diff import diff_snapshot_with_env
from envforge.history import record_event


def current_env() -> dict:
    return dict(os.environ)


def watch_env(
    snapshot_dir: str,
    name: str,
    interval: int = 5,
    max_iterations: Optional[int] = None,
    auto_save: bool = False,
) -> None:
    """
    Poll the environment every `interval` seconds and report changes
    compared to the named snapshot. If auto_save is True, save a new
    snapshot whenever a change is detected.
    """
    iteration = 0
    print(f"Watching environment against snapshot '{name}' (interval={interval}s)")

    while True:
        diff = diff_snapshot_with_env(snapshot_dir, name)
        if diff.has_changes():
            print(f"[{time.strftime('%H:%M:%S')}] Changes detected:")
            print(diff.summary())
            if auto_save:
                env = current_env()
                save_snapshot(snapshot_dir, name, env)
                record_event(snapshot_dir, name, "watch-autosave")
                print(f"  → Auto-saved snapshot '{name}'")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] No changes.")

        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            break
        time.sleep(interval)

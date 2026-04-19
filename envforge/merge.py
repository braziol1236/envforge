"""Merge two snapshots into a new one."""
from typing import Optional
from envforge.snapshot import load_snapshot, save_snapshot


def merge_snapshots(
    base_name: str,
    overlay_name: str,
    output_name: str,
    snapshot_dir: Optional[str] = None,
    overwrite: bool = False,
) -> dict:
    """
    Merge overlay snapshot on top of base snapshot.
    Keys in overlay take precedence over base.
    Returns the merged env dict.
    """
    base = load_snapshot(base_name, snapshot_dir=snapshot_dir)
    overlay = load_snapshot(overlay_name, snapshot_dir=snapshot_dir)

    merged_env = {**base["env"], **overlay["env"]}

    merged_snapshot = {
        "name": output_name,
        "env": merged_env,
        "merged_from": [base_name, overlay_name],
    }

    save_snapshot(output_name, merged_env, snapshot_dir=snapshot_dir, extra={
        "merged_from": [base_name, overlay_name]
    })

    return merged_snapshot


def merge_with_env(
    base_name: str,
    output_name: str,
    env_overrides: dict,
    snapshot_dir: Optional[str] = None,
) -> dict:
    """
    Merge a snapshot with a dict of env overrides (e.g. from os.environ).
    Overrides take precedence.
    """
    base = load_snapshot(base_name, snapshot_dir=snapshot_dir)
    merged_env = {**base["env"], **env_overrides}

    save_snapshot(output_name, merged_env, snapshot_dir=snapshot_dir, extra={
        "merged_from": [base_name, "<env>"]
    })

    return {"name": output_name, "env": merged_env}

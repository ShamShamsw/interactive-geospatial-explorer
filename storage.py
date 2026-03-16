"""
storage.py - Persistence helpers for geospatial run artifacts
=============================================================
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
RUNS_DIR = DATA_DIR / "runs"
OUTPUTS_DIR = DATA_DIR / "outputs"

LATEST_RUN = RUNS_DIR / "latest_geospatial_run.json"
RUN_HISTORY = RUNS_DIR / "geospatial_run_history.json"


def ensure_storage_dirs() -> None:
    """Create all required storage directories if missing."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    """
    Read JSON from disk with a safe default fallback.
    """
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, payload) -> None:
    """Write JSON payload in a readable format."""
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_latest_run(run: dict) -> None:
    """
    Save the latest run and append to historical run log.

    Parameters:
        run (dict): Full run artifact payload.
    """
    ensure_storage_dirs()
    _write_json(LATEST_RUN, run)

    history = _read_json(RUN_HISTORY, default=[])
    history.append(run)
    _write_json(RUN_HISTORY, history)


def load_latest_run() -> dict:
    """Load latest geospatial run artifact."""
    ensure_storage_dirs()
    return _read_json(LATEST_RUN, default={})


def get_output_dir() -> Path:
    """Return folder where HTML map outputs should be stored."""
    ensure_storage_dirs()
    return OUTPUTS_DIR

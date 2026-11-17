"""JSON persistence for the gradebook."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PATH = BASE_DIR / "data" / "gradebook.json"


def empty_data():
    """Return a new, empty gradebook structure."""
    return {"students": [], "courses": [], "enrollments": []}


def load_data(path=DEFAULT_PATH):
    """Load gradebook data, starting empty if the file does not exist."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        logger.info("No data file at %s; starting empty", path)
        return empty_data()
    except json.JSONDecodeError as exc:
        message = (
            f"Could not read {path}: invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}. Fix or delete the file and try again."
        )
        logger.error(message)
        raise ValueError(message) from exc
    except OSError as exc:
        logger.error("Could not open %s: %s", path, exc)
        raise
    if not isinstance(data, dict):
        message = f"Could not read {path}: expected a JSON object."
        logger.error(message)
        raise ValueError(message)
    for key, default in empty_data().items():
        data.setdefault(key, default)
    logger.info("Loaded data from %s", path)
    return data


def save_data(data, path=DEFAULT_PATH):
    """Write gradebook data to a JSON file."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except OSError as exc:
        logger.error("Could not save %s: %s", path, exc)
        raise
    logger.info("Saved data to %s", path)

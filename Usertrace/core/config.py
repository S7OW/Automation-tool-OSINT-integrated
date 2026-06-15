from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Union

from core.constants import CONFIG_FILE, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT

DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "timeout": DEFAULT_TIMEOUT,
        "user_agent": DEFAULT_USER_AGENT,
        "debug": False,
    },
    "output": {
        "logs": "logs",
        "exports": "exports",
    },
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}

    try:
        with path.open("r", encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file) or {}
    except (OSError, yaml.YAMLError):
        return {}

    return data if isinstance(data, dict) else {}


def _merge_dicts(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)

    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value

    return merged


def load_config(path: Union[str, Path] = CONFIG_FILE) -> Dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)

    return _merge_dicts(DEFAULT_CONFIG, _load_yaml(config_path))

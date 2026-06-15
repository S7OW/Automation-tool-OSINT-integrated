from importlib import import_module
from typing import Callable, Dict, List

from core.constants import STATUS_ERROR
from core.interface import create_result

ModuleCheck = Callable[..., Dict[str, object]]

USERNAME_MODULE_NAMES = [
    "github",
    "reddit",
    "tiktok",
    "instagram",
    "pinterest",
    "twitter",
    "facebook",
    "steam",
    "twitch",
    "youtube",
    "linkedin",
    "medium",
    "telegram",
    "gitlab",
    "behance",
    "deviantart",
    "soundcloud",
    "vimeo",
    "hackernews",
]

MODULE_REGISTRY = {
    "username": USERNAME_MODULE_NAMES,
}


def get_modules(trace_name: str) -> List[ModuleCheck]:
    return [_load_module_check(module_name) for module_name in MODULE_REGISTRY.get(trace_name, [])]


def _load_module_check(module_name: str) -> ModuleCheck:
    try:
        module = import_module(f"modules.{module_name}")
        check = getattr(module, "check")
        return check
    except Exception as exc:
        return _broken_module_check(module_name, exc)


def _broken_module_check(module_name: str, error: Exception) -> ModuleCheck:
    platform = module_name.replace("_", " ").title()

    def check(target: str, **_: object) -> Dict[str, object]:
        result = create_result(platform, STATUS_ERROR, str(target), 0.0)
        result["error"] = str(error)
        return result

    check.platform = platform
    return check

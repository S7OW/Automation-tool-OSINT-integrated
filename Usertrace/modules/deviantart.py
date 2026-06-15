from core.constants import DEFAULT_TIMEOUT
from core.interface import ResultSchema
from modules._username import blocked_safe_status, check_profile, normalize_username

PLATFORM = "DeviantArt"
BASE_URL = "https://www.deviantart.com/{username}"


def check(username: str, timeout: float = DEFAULT_TIMEOUT, **_: object) -> ResultSchema:
    clean_username = normalize_username(username)
    return check_profile(
        platform=PLATFORM,
        url=BASE_URL.format(username=clean_username),
        status_resolver=blocked_safe_status,
        timeout=timeout,
    )


check.platform = PLATFORM

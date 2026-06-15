from core.constants import DEFAULT_TIMEOUT
from core.interface import ResultSchema
from modules._username import basic_profile_status, check_profile, normalize_username

PLATFORM = "Instagram"
BASE_URL = "https://www.instagram.com/{username}/"


def check(username: str, timeout: float = DEFAULT_TIMEOUT, **_: object) -> ResultSchema:
    clean_username = normalize_username(username, strip_at=True)
    return check_profile(
        platform=PLATFORM,
        url=BASE_URL.format(username=clean_username),
        status_resolver=basic_profile_status,
        timeout=timeout,
    )


check.platform = PLATFORM

from core.constants import DEFAULT_TIMEOUT
from core.interface import ResultSchema
from modules._username import check_profile, normalize_username, status_from_code

PLATFORM = "GitHub"
BASE_URL = "https://github.com/{username}"


def check(username: str, timeout: float = DEFAULT_TIMEOUT, **_: object) -> ResultSchema:
    clean_username = normalize_username(username)
    return check_profile(
        platform=PLATFORM,
        url=BASE_URL.format(username=clean_username),
        status_resolver=status_from_code,
        timeout=timeout,
    )


check.platform = PLATFORM

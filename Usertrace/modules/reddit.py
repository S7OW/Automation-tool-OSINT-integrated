from core.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from core.interface import ResultSchema
from modules._username import check_profile, normalize_username, status_from_code

PLATFORM = "Reddit"
BASE_URL = "https://www.reddit.com/user/{username}/"


def check(username: str, timeout: float = DEFAULT_TIMEOUT, **_: object) -> ResultSchema:
    clean_username = normalize_username(username)
    return check_profile(
        platform=PLATFORM,
        url=BASE_URL.format(username=clean_username),
        status_resolver=status_from_code,
        timeout=timeout,
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )


check.platform = PLATFORM

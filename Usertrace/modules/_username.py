from time import perf_counter
from typing import Callable, Dict, Optional
from urllib.parse import quote

import requests

from core.constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    STATUS_ERROR,
    STATUS_FOUND,
    STATUS_NOT_FOUND,
    STATUS_PRIVATE,
)
from core.interface import ResultSchema, create_result

StatusResolver = Callable[[requests.Response], str]


def normalize_username(username: str, strip_at: bool = False) -> str:
    clean_username = str(username).strip()
    if strip_at:
        clean_username = clean_username.lstrip("@")
    return quote(clean_username, safe="")


def check_profile(
    platform: str,
    url: str,
    status_resolver: StatusResolver,
    timeout: float = DEFAULT_TIMEOUT,
    headers: Optional[Dict[str, str]] = None,
) -> ResultSchema:
    started = perf_counter()
    request_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        request_headers.update(headers)

    try:
        with requests.Session() as session:
            session.headers.update(request_headers)
            response = session.get(url, timeout=timeout, allow_redirects=True)
            status = status_resolver(response)
    except Exception:
        status = STATUS_ERROR

    return create_result(
        platform=platform,
        status=status,
        url=url,
        response_time=perf_counter() - started,
    )


def status_from_code(response: requests.Response) -> str:
    if response.status_code == 200:
        return STATUS_FOUND
    if response.status_code in (404, 410):
        return STATUS_NOT_FOUND
    return STATUS_ERROR


def basic_profile_status(response: requests.Response) -> str:
    if response.status_code in (404, 410):
        return STATUS_NOT_FOUND
    if response.status_code != 200:
        return STATUS_ERROR

    page_text = response.text.lower()
    private_markers = (
        "this account is private",
        "account is private",
        "private account",
        "this profile is private",
    )

    if any(marker in page_text for marker in private_markers):
        return STATUS_PRIVATE

    return STATUS_FOUND


def blocked_safe_status(response: requests.Response) -> str:
    if response.status_code in (404, 410):
        return STATUS_NOT_FOUND
    if response.status_code in (401, 403, 429, 503):
        return STATUS_ERROR
    if response.status_code == 200:
        return STATUS_FOUND
    return STATUS_ERROR

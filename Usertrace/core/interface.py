from typing import Dict, Literal, TypedDict

from core.constants import (
    STATUS_ERROR,
    STATUS_FOUND,
    STATUS_NOT_FOUND,
    STATUS_PRIVATE,
    VALID_STATUSES,
)

Status = Literal["FOUND", "NOT FOUND", "PRIVATE", "ERROR"]


class ResultSchema(TypedDict):
    platform: str
    status: Status
    url: str
    response_time: float


def create_result(
    platform: str,
    status: str,
    url: str = "",
    response_time: float = 0.0,
) -> ResultSchema:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    return {
        "platform": str(platform),
        "status": status,  # type: ignore[typeddict-item]
        "url": str(url),
        "response_time": float(response_time),
    }


__all__ = [
    "ResultSchema",
    "Status",
    "create_result",
    "STATUS_FOUND",
    "STATUS_NOT_FOUND",
    "STATUS_PRIVATE",
    "STATUS_ERROR",
]

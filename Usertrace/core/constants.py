from pathlib import Path

APP_NAME = "UserTrace"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.yaml"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "usertrace.log"
EXPORT_DIR = BASE_DIR / "exports"
DATABASE_DIR = BASE_DIR / "databases"
DATABASE_FILE = DATABASE_DIR / "history.db"

STATUS_FOUND = "FOUND"
STATUS_NOT_FOUND = "NOT FOUND"
STATUS_PRIVATE = "PRIVATE"
STATUS_ERROR = "ERROR"

VALID_STATUSES = {
    STATUS_FOUND,
    STATUS_NOT_FOUND,
    STATUS_PRIVATE,
    STATUS_ERROR,
}

SUPPORTED_COMMANDS = (
    "username",
    "email",
    "domain",
    "link",
    "metadata",
    "web",
)

DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = f"{APP_NAME}/{APP_VERSION}"

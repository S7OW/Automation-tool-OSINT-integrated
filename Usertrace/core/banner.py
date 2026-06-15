from core.constants import APP_NAME, APP_VERSION

BANNER = r"""
 _   _              _____                    
| | | |___  ___ _ _|_   _| __ __ _  ___ ___ 
| | | / __|/ _ \ '__|| || '__/ _` |/ __/ _ \
| |_| \__ \  __/ |   | || | (_| | (_|  __/
 \___/|___/\___|_|   |_||_|  \__,_|\___\___|
"""


def print_banner() -> None:
    text = f"{BANNER}\n{APP_NAME} v{APP_VERSION}"

    try:
        from rich.console import Console
        from rich.text import Text
    except ImportError:
        print(f"\033[36m{text}\033[0m")
        return

    Console().print(Text(text, style="cyan"))

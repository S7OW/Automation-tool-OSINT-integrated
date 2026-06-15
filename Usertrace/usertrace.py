import argparse
import json
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List

from core.banner import print_banner
from core.config import load_config
from core.constants import APP_NAME, DATABASE_DIR, EXPORT_DIR, LOG_DIR, STATUS_ERROR, SUPPORTED_COMMANDS
from core.database import HistoryDatabase
from core.exporter import export_results
from core.interface import create_result
from core.logger import setup_logger

STATUS_STYLES = {
    "FOUND": "green",
    "NOT FOUND": "red",
    "PRIVATE": "yellow",
    "ERROR": "magenta",
}


def _stub_result(command: str, target: str) -> Dict[str, Any]:
    return create_result(
        platform=command,
        status=STATUS_ERROR,
        url=target,
        response_time=0.0,
    )


def _username_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("username", target)


def _email_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("email", target)


def _domain_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("domain", target)


def _link_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("link", target)


def _metadata_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("metadata", target)


def _web_stub(target: str, options: argparse.Namespace) -> Dict[str, Any]:
    return _stub_result("web", target)


_PLACEHOLDER_ROUTES = {
    "username": _username_stub,
    "email": _email_stub,
    "domain": _domain_stub,
    "link": _link_stub,
    "metadata": _metadata_stub,
    "web": _web_stub,
}


def _placeholder_route(command: str, target: str, options: argparse.Namespace) -> Dict[str, Any]:
    handler = _PLACEHOLDER_ROUTES.get(command)
    if handler is None:
        return _stub_result(command, target)
    return handler(target, options)


def _get_router() -> Callable[[str, str, argparse.Namespace], Dict[str, Any]]:
    try:
        from core.router import route_command
    except ImportError:
        return _placeholder_route

    return route_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="usertrace",
        description="UserTrace OSINT framework core CLI.",
    )
    parser.set_defaults(no_banner=False, json=False, open=False, export=None, threads=10, timeout=10.0)
    _add_common_options(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in SUPPORTED_COMMANDS:
        command_parser = subparsers.add_parser(
            command,
            help=f"Run {command} trace.",
        )
        command_parser.add_argument(
            "target",
            help=f"{command} target to trace.",
        )
        _add_common_options(command_parser)

    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--no-banner",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Do not display the startup banner.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Print command output as JSON.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Open FOUND result URLs in the default browser.",
    )
    parser.add_argument(
        "--export",
        choices=("json", "csv", "txt"),
        default=argparse.SUPPRESS,
        help="Export scan results to exports/ in the selected format.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=argparse.SUPPRESS,
        help="Number of worker threads to use.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=argparse.SUPPRESS,
        help="HTTP timeout per request in seconds.",
    )


def run_command(args: argparse.Namespace) -> Dict[str, Any]:
    load_config()
    logger = setup_logger()
    router = _get_router()

    logger.info("Command received: %s target=%s", args.command, args.target)
    result = router(args.command, args.target, args)
    logger.info("Command completed: %s result=%s", args.command, result)

    return result


def run_with_progress(args: argparse.Namespace) -> Dict[str, Any]:
    if args.json:
        return run_command(args)

    try:
        from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    except ImportError:
        return _run_with_plain_loading(args)

    result: Dict[str, Any] = {}
    error: List[BaseException] = []

    def worker() -> None:
        try:
            result.update(run_command(args))
        except BaseException as exc:
            error.append(exc)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task_id = progress.add_task("Searching.", total=None)
        dots = 1
        while thread.is_alive():
            dots = 1 if dots == 3 else dots + 1
            progress.update(task_id, description=f"Searching{'.' * dots}")
            time.sleep(0.3)

    thread.join()
    if error:
        raise error[0]
    return result


def _run_with_plain_loading(args: argparse.Namespace) -> Dict[str, Any]:
    print("Searching...", flush=True)
    return run_command(args)


def persist_results(args: argparse.Namespace, result: Dict[str, Any]) -> None:
    if args.command not in {"username", "email", "domain"}:
        return

    try:
        HistoryDatabase().insert_many(args.command, args.target, result.get("results", []))
    except Exception as exc:
        setup_logger().error("Database persistence failed: %s", exc)


def export_scan(args: argparse.Namespace, result: Dict[str, Any]) -> Path:
    filename = f"{args.command}_{_safe_filename(args.target)}"
    return export_results(result, args.export, filename)


def open_found_results(result: Dict[str, Any]) -> int:
    opened = 0
    for row in result.get("results", []):
        url = str(row.get("url", ""))
        if row.get("status") == "FOUND" and url.startswith(("http://", "https://")):
            webbrowser.open(url)
            opened += 1
    return opened


def render_result(result: Dict[str, Any], export_path: Path = None, opened: int = 0) -> None:
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        print(json.dumps(result, indent=2))
        if export_path:
            print(f"Exported: {export_path}")
        if opened:
            print(f"Opened URLs: {opened}")
        return

    console = Console()
    table = Table(title=f"{APP_NAME} Results")
    table.add_column("Platform", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("URL")
    table.add_column("Time", justify="right")

    for row in result.get("results", []):
        status = str(row.get("status", "ERROR"))
        style = STATUS_STYLES.get(status, "magenta")
        table.add_row(
            str(row.get("platform", "")),
            f"[{style}]{status}[/{style}]",
            str(row.get("url", "")),
            f"{float(row.get('response_time', 0.0)):.2f}s",
        )

    if not result.get("results"):
        table.add_row("No results", "[magenta]ERROR[/magenta]", str(result.get("target", "")), "0.00s")

    console.print(table)
    console.print(
        f"[bold]{result.get('command')}[/bold] target: [cyan]{result.get('target')}[/cyan] "
        f"({result.get('count', 0)} results)"
    )
    if export_path:
        console.print(f"[green]Exported:[/green] {export_path}")
    if opened:
        console.print(f"[green]Opened URLs:[/green] {opened}")


def ensure_runtime_dirs() -> None:
    for path in (LOG_DIR, EXPORT_DIR, DATABASE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _safe_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value)
    return safe[:80] or "target"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    ensure_runtime_dirs()

    if not args.no_banner:
        print_banner()

    result = run_with_progress(args)
    persist_results(args, result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        export_path = export_scan(args, result) if args.export else None
        opened = open_found_results(result) if args.open else 0
        render_result(result, export_path, opened)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

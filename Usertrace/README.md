# UserTrace

```text
 _   _              _____
| | | |___  ___ _ _|_   _| __ __ _  ___ ___
| | | / __|/ _ \ '__|| || '__/ _` |/ __/ _ \
| |_| \__ \  __/ |   | || | (_| | (_|  __/
 \___/|___/\___|_|   |_||_|  \__,_|\___\___|
```

**UserTrace** is a Python OSINT framework for username, email, domain, link, metadata, and web reconnaissance. It provides a clean command-line workflow, concurrent scanning, standardized results, export support, and local history tracking for repeat investigations.

## Features

### UsernameTrace

Searches for usernames across multiple public platforms using a modular scanner architecture. Current modules include GitHub, Reddit, TikTok, Instagram, Pinterest, Twitter, Facebook, Steam, Twitch, YouTube, LinkedIn, Medium, Telegram, GitLab, Behance, DeviantArt, SoundCloud, Vimeo, and Hacker News.

### EmailTrace

Performs basic email intelligence:

- Email format validation
- Domain extraction
- Gravatar profile check when reachable

### DomainTrace

Runs domain reconnaissance:

- WHOIS lookup
- DNS record analysis
- A/IP resolution
- MX records
- NS records

### LinkTrace

Inspects URLs and follows redirects:

- Final destination URL
- Redirect chain
- HTTP status code
- Response headers
- HTML title extraction

### MetadataTrace

Extracts file metadata safely from supported file types:

- JPG/JPEG
- PNG
- PDF
- DOCX

Metadata extraction uses optional libraries when available and fails gracefully when dependencies are missing or files are unsupported.

### WebTrace

Detects web technologies from headers and HTML patterns:

- Server headers
- `X-Powered-By`
- WordPress indicators
- React and Next.js indicators
- jQuery and Bootstrap indicators
- Cloudflare and analytics markers

### Core Capabilities

- Multithreaded scanning with `ThreadPoolExecutor`
- JSON, CSV, and TXT export system
- SQLite history tracking
- Rich terminal UI with colored result tables
- Modular plugin-style architecture
- Safe exception handling across scanners and trace modules
- Configurable threads and timeout values

## Installation

UserTrace requires **Python 3.9+**.

Clone or download the project, then install dependencies:

```bash
pip install -r requirements.txt
```

Some OSINT features use optional third-party packages such as `dnspython`, `python-whois`, `Pillow`, and `exifread`. The framework is designed to fail gracefully if optional dependencies are unavailable.

## Usage

Run UserTrace from the project root:

```bash
python usertrace.py username johndoe
python usertrace.py email test@gmail.com
python usertrace.py domain example.com
python usertrace.py link https://example.com
python usertrace.py metadata file.jpg
python usertrace.py web example.com
```

### Optional Flags

Export results:

```bash
python usertrace.py username johndoe --export json
python usertrace.py username johndoe --export csv
python usertrace.py username johndoe --export txt
```

Tune concurrency and request timeout:

```bash
python usertrace.py username johndoe --threads 50 --timeout 5
```

Open found profile URLs in the default browser:

```bash
python usertrace.py username johndoe --open
```

Print raw JSON output:

```bash
python usertrace.py username johndoe --json
```

Disable the startup banner:

```bash
python usertrace.py username johndoe --no-banner
```

Flags can be combined:

```bash
python usertrace.py username johndoe --threads 50 --timeout 5 --export json --open
```

## Output Example

UserTrace renders scan results in a Rich terminal table:

```text
                              UserTrace Results
+---------------------------------------------------------------------+
| Platform    | Status    | URL                              |  Time |
|-------------+-----------+----------------------------------+-------|
| GitHub      | FOUND     | https://github.com/johndoe       | 0.42s |
| Reddit      | NOT FOUND | https://www.reddit.com/user/...  | 0.51s |
| TikTok      | PRIVATE   | https://www.tiktok.com/@johndoe  | 0.66s |
| LinkedIn    | ERROR     | https://www.linkedin.com/in/...  | 0.88s |
+---------------------------------------------------------------------+
username target: johndoe (4 results)
```

Status colors:

- `FOUND` is green
- `NOT FOUND` is red
- `PRIVATE` is yellow
- `ERROR` is magenta

## Architecture

UserTrace is organized around a clean separation between routing, trace workflows, scanning, platform modules, persistence, and output.

```text
UserTrace/
├── core/
├── modules/
├── traces/
├── utils/
├── exports/
├── databases/
├── logs/
├── requirements.txt
└── usertrace.py
```

### `core/`

Core framework services:

- CLI routing
- Scanner engine
- Result schema and result storage
- Export system
- SQLite persistence
- Logging
- Configuration
- Banner and terminal support

### `modules/`

Platform-specific username lookup modules. Each module exposes a consistent `check()` function and returns the standard UserTrace result schema:

```python
{
    "platform": str,
    "status": "FOUND | NOT FOUND | PRIVATE | ERROR",
    "url": str,
    "response_time": float
}
```

This structure makes it straightforward to add new platforms without changing the scanner engine.

### `traces/`

High-level reconnaissance workflows:

- `UsernameTrace`
- `EmailTrace`
- `DomainTrace`
- `LinkTrace`
- `MetadataTrace`
- `WebTrace`

Trace classes decide which modules or checks to run, then return centralized `ScanResults`.

### `utils/`

Utility code for future helpers, validators, browser handling, animation helpers, and terminal-related functionality.

### `exports/`

Generated export files are written here. Supported formats:

- JSON
- CSV
- TXT

### `databases/`

SQLite history database location:

```text
databases/history.db
```

The database stores scan history including target identifiers, platform, status, URL, and timestamp.

### Modular Plugin Architecture

UserTrace modules are intentionally small and consistent. A platform module only needs to provide a callable that accepts a target and returns the standardized result schema. The scanner can then execute it concurrently with the rest of the module set.

This design allows new modules to be added with minimal friction:

1. Create a new file in `modules/`.
2. Implement a `check(target, timeout=...)` function.
3. Return the standard schema.
4. Register the function in the relevant trace workflow.

## Technical Details

### ThreadPoolExecutor

The core scanner uses Python's `ThreadPoolExecutor` to run module functions concurrently. This keeps username reconnaissance fast while preserving a simple synchronous module API.

### requests.Session

HTTP-based modules use `requests.Session()` for connection reuse, consistent headers, timeout handling, and safe cleanup.

### Retry Handling

The current framework is structured for retry support through configuration values such as `retry_count`. Platform modules safely handle request errors, blocking, rate limiting, and unexpected exceptions by returning standardized `ERROR` results instead of crashing the scan.

### SQLite Logging System

UserTrace records scan history in SQLite at:

```text
databases/history.db
```

Stored fields include:

- `username`
- `email`
- `domain`
- `platform`
- `status`
- `url`
- `timestamp`

SQL operations use parameterized queries and the database is created automatically when missing.

### config.yaml System

UserTrace can load settings from `config.yaml` when present. If the file is missing, the framework uses safe defaults. This allows the project to run immediately after installation while still supporting environment-specific tuning.

## Configuration

Example `config.yaml`:

```yaml
threads: 50
timeout: 5
theme: hacker
retry_count: 3
open_browser: false
```

Recommended values depend on network conditions and target platform behavior. Higher thread counts can improve speed but may increase rate limiting or blocking from some platforms.

## Roadmap

Planned improvements:

- Proxy rotation system
- Async engine upgrade
- GUI version
- Plugin marketplace
- AI OSINT correlation engine

## Disclaimer

UserTrace is provided for educational and authorized security research purposes only.

Use this framework responsibly:

- Respect platform terms of service.
- Do not attempt unauthorized access.
- Do not use UserTrace for harassment, stalking, abuse, or illegal activity.
- Only investigate assets, accounts, files, or infrastructure you own or have explicit permission to assess.

The maintainers and contributors are not responsible for misuse of this software.

## License

MIT License

Copyright (c) 2026 UserTrace

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions of the MIT License.

The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from the software or the use of the software.

# ODIX - Automation and Integrated OSINT Toolkit

By Amine Azr

ODIX is a Python command-line menu that groups automation and OSINT utilities in one place. The current build includes an email discovery/outreach workflow powered by Hunter.io and an integrated UserTrace OSINT framework for username, email, domain, link, metadata, and web reconnaissance.

This project is intended for education, authorized research, and legitimate automation only.

## Current Tool Status

| Menu option | Tool | Status | Description |
| --- | --- | --- | --- |
| `1` | Email Automation Tool | Available | Finds emails for a configured domain with Hunter.io, filters likely decision makers, and sends personalized outreach emails with SMTP. |
| `2` | Brute Force | Not available | Placeholder only. The current script prints a "not ready yet" message. |
| `3` | UserTrace | Available | Opens the bundled UserTrace OSINT CLI from the `Usertrace/` folder. |
| `4` | DoS attack | Not available | Placeholder only. The current script prints a "not ready yet" message. |
| `0` | Exit | Available | Exits the menu. |

## Project Structure

```text
.
|-- odix.py
|-- README.md
|-- LICENSE
`-- Usertrace/
    |-- usertrace.py
    |-- requirements.txt
    |-- core/
    |-- traces/
    |-- modules/
    |-- utils/
    |-- exports/
    |-- databases/
    `-- logs/
```

## Requirements

- Python 3.9 or newer
- Internet access for Hunter.io, SMTP, and public OSINT checks
- A Hunter.io API key for the email automation tool
- SMTP credentials if you want ODIX to send outreach emails

Install UserTrace dependencies:

```bash
pip install -r Usertrace/requirements.txt
```

The root `odix.py` also uses `requests`, which is included in `Usertrace/requirements.txt`.

## How To Run ODIX

From the project root:

```bash
python odix.py
```

Then choose a menu option:

```text
1. Email Automation Tool
2. Brute Force
3. UserTrace
4. Dos attack
0. Exit
```

## Tool 1: Email Automation Tool

The email automation tool is built directly into `odix.py`.

### Features

- Searches a target domain for email addresses using the Hunter.io Domain Search API.
- Filters contacts by seniority and job title to prioritize likely decision makers.
- Sends personalized emails through SMTP.
- Uses a simple email template with first and last name placeholders.
- Waits briefly between emails to reduce the chance of triggering spam or rate-limit controls.

### Configuration

Before running option `1`, edit the configuration section in `odix.py`:

```python
HUNTER_API_KEY = "your_hunter_api_key"
TARGET_DOMAIN = "instagram.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_gmail@gmail.com"
SMTP_PASSWORD = "your_gmail_app_password"
YOUR_EMAIL = "your_gmail@gmail.com"

EMAIL_SUBJECT = "Your e-mail subject here"
EMAIL_BODY_TEMPLATE = """Dear {first_name} {last_name},
...
"""
```

For Gmail, use an app password instead of your normal account password.

### Usage

1. Open `odix.py`.
2. Set `HUNTER_API_KEY`, `TARGET_DOMAIN`, SMTP credentials, subject, and email body.
3. Run:

```bash
python odix.py
```

4. Choose option `1`.

### Important Notes

- The Tool won't work if you did not replace the config with your own one
- The script can send real emails. Test with your own address first.
- Hunter.io and your SMTP provider may enforce usage limits "10 e-mails", account rules, and anti-abuse controls.

## Tool 3: UserTrace

UserTrace is bundled in the `Usertrace/` folder and is launched from ODIX menu option `3`.

When you choose option `3`, ODIX opens a UserTrace submenu:

```text
1. username
2. email
3. domain
4. link
5. metadata
6. web
0. Back
```

After selecting a trace type, enter the target and optional UserTrace flags.

### UserTrace Features

- `username`: Searches for a username across supported public platforms.
- `email`: Validates email format, extracts the domain, and checks for Gravatar information when reachable.
- `domain`: Performs DNS and WHOIS-style domain reconnaissance.
- `link`: Follows redirects and collects basic URL response information.
- `metadata`: Extracts metadata from supported local files such as images, PDFs, and DOCX files.
- `web`: Detects basic web technologies from headers and HTML patterns.
- Export support for `json`, `csv`, and `txt`.
- Optional JSON output.
- Optional browser opening for found profile URLs.
- Local history storage for username, email, and domain results.
- Logs stored in `Usertrace/logs/`.

### UserTrace Usage Through ODIX

```bash
python odix.py
```

Choose option `3`, then choose a trace type.

Examples:

```text
Select a tool: 3
Select a trace type: 1
Enter username target: johndoe
Optional flags: --export json
```

```text
Select a tool: 3
Select a trace type: domain
Enter domain target: example.com
Optional flags: --json
```

### UserTrace Direct CLI Usage

You can also run UserTrace directly:

```bash
cd Usertrace
python usertrace.py username johndoe
python usertrace.py email test@example.com
python usertrace.py domain example.com
python usertrace.py link https://example.com
python usertrace.py metadata file.jpg
python usertrace.py web example.com
```

Useful flags:

```bash
python usertrace.py username johndoe --export json
python usertrace.py username johndoe --export csv
python usertrace.py username johndoe --open
python usertrace.py username johndoe --json
python usertrace.py username johndoe --threads 50 --timeout 5
python usertrace.py username johndoe --no-banner
```

## Data Storage

ODIX and UserTrace may create or use local files:

- `Usertrace/logs/usertrace.log`: UserTrace command logs.
- `Usertrace/exports/`: Exported scan results.
- `Usertrace/databases/history.db`: SQLite history for selected trace results.
- `Usertrace/config.yaml`: Optional local configuration file if you create one.

Review these files before sharing the project folder because they may contain targets, scan results, timestamps, or other sensitive investigation details.

## Security And Privacy

- Do not store real API keys or SMTP passwords in public repositories.
- Prefer environment variables or a private local config if you extend the project.
- Do not scan, profile, contact, or collect data about people without a lawful and ethical reason.
- Do not send bulk unsolicited email.
- Do not use collected emails for spam, phishing, harassment, impersonation, or credential attacks.
- Do not publish scan results that contain personal data unless you have permission.
- Treat exported results, logs, and history databases as sensitive.
- Keep dependencies updated and install them from trusted sources.

## Responsible Use

Use this toolkit only for:

- Your own accounts, domains, files, and infrastructure, or at least ethical use
- Authorized security research.
- Legitimate business outreach that follows applicable laws and platform rules.
- Education and controlled demonstrations.

Do not use this toolkit for:

- Unauthorized access attempts.
- Harassment, stalking, doxxing, or intimidation.
- Spam or deceptive outreach.
- Denial-of-service activity.
- Password attacks or credential stuffing.
- Bypassing platform restrictions or terms of service.

The Brute Force and DoS menu entries are intentionally not implemented in the current version. They should not be used or extended for illegal activity.

## Troubleshooting

### ODIX banner does not display correctly

Use a UTF-8 capable terminal. Recent versions of `odix.py` also configure stdout and stderr as UTF-8 when possible.

### Hunter.io returns no emails

Check your API key, target domain, Hunter.io quota, and the domain's public email availability.

### SMTP authentication fails

Check your SMTP username, server, port, and app password. Gmail requires app passwords for this type of script.

### UserTrace optional features fail

Install dependencies:

```bash
pip install -r Usertrace/requirements.txt
```

Some features depend on optional packages such as `dnspython`, `python-whois`, `Pillow`, and `exifread`.

## Roadmap Ideas

- Move secrets out of `odix.py` and into environment variables or a local ignored config file.
- Add a safer dry-run mode for the email tool.
- Add confirmation before sending outreach emails.
- Add a main requirements file for the whole project.
- Add tests for menu routing and UserTrace integration.
- Replace placeholder menu options with clearly scoped, legal, defensive tools.

## License

This project is released under the MIT License. See `LICENSE` for details.

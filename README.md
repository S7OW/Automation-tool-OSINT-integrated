# Odix — Hunter.io Email Discovery & Outreach Tool

Small Python utility to discover email addresses for a target domain (via Hunter.io) and send personalized outreach emails.

## Features
- Search a domain for email addresses using the Hunter.io Domain Search API
- Filter results to prioritize decision-makers by seniority/position
- Send personalized email outreach via SMTP

## Quick Start
1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure credentials:

- `HUNTER_API_KEY` — your Hunter.io API key
- `SMTP_USER` — SMTP username (email)
- `SMTP_PASSWORD` — SMTP app password
- `YOUR_EMAIL` — your contact email used in messages

## Usage
Run the script:

```bash
python odix.py
```

Follow the menu to run the Email Automation Tool.

## Security & Privacy Notes
- DO NOT commit API keys, SMTP passwords, or other secrets to source control.
- Prefer environment variables or a separate config file excluded by `.gitignore`.
- Be aware of legal and ethical constraints when collecting and contacting addresses. Only contact people you are authorized to contact.

## Responsible Use
This tool can be used to send real emails. Misuse may violate terms of service, privacy laws, and anti-spam regulations. By using or publishing this repository you agree to follow all applicable laws and to use the tool ethically.

## License
This project is released under the MIT License — see `LICENSE`

---
You can use the tool in some other kind of automations if you know how to edit it
---

This tool will have more tools inside it in the future if i find that there is people interesed in what i'm giving.


import os
import shlex
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
USERTRACE_DIR = BASE_DIR / "Usertrace"
USERTRACE_SCRIPT = USERTRACE_DIR / "usertrace.py"
USERTRACE_COMMANDS = ("username", "email", "domain", "link", "metadata", "web")


try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def run_usertrace_tool():
    """Launch the bundled UserTrace CLI from the ODIX menu."""
    if not USERTRACE_SCRIPT.exists():
        print(f"[ERROR] UserTrace was not found at: {USERTRACE_SCRIPT}")
        input("Press Enter to return to the ODIX menu...")
        return

    print("=" * 60)
    print("UserTrace")
    print("=" * 60)
    print("Available traces:")
    for index, command in enumerate(USERTRACE_COMMANDS, 1):
        print(f"{index}. {command}")
    print("0. Back")

    trace_choice = input("Select a trace type: ").strip().lower()
    if trace_choice == "0":
        return

    if trace_choice.isdigit() and 1 <= int(trace_choice) <= len(USERTRACE_COMMANDS):
        command = USERTRACE_COMMANDS[int(trace_choice) - 1]
    elif trace_choice in USERTRACE_COMMANDS:
        command = trace_choice
    else:
        print("[ERROR] Invalid UserTrace option.")
        input("Press Enter to return to the ODIX menu...")
        return

    target = input(f"Enter {command} target: ").strip()
    if not target:
        print("[ERROR] Target is required.")
        input("Press Enter to return to the ODIX menu...")
        return

    extra_args = input(
        "Optional flags, e.g. --export json --open --threads 50 (press Enter to skip): "
    ).strip()

    cmd = [sys.executable, str(USERTRACE_SCRIPT), command, target]
    if extra_args:
        try:
            cmd.extend(shlex.split(extra_args, posix=(os.name != "nt")))
        except ValueError as exc:
            print(f"[ERROR] Could not parse optional flags: {exc}")
            input("Press Enter to return to the ODIX menu...")
            return

    print("\n[START] Launching UserTrace...\n")
    try:
        subprocess.run(cmd, cwd=USERTRACE_DIR, check=False)
    except OSError as exc:
        print(f"[ERROR] Failed to launch UserTrace: {exc}")

    input("\nPress Enter to return to the ODIX menu...")

def show_odix_panel():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print(r"""
   ██████╗ ██████╗ ██╗██╗  ██╗
  ██╔═══██╗██╔══██╗██║╚██╗██╔╝
  ██║   ██║██║  ██║██║ ╚███╔╝
  ██║   ██║██║  ██║██║ ██╔██╗
  ╚██████╔╝██████╔╝██║██╔╝ ██╗
   ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═╝
    """)
    print("=" * 60)
    print("1. Email Automation Tool")
    print("2. Brute Force")
    print("3. UserTrace")
    print("4. Dos attack")
    print("0. Exit")
    choice = input("Select a tool: ")
    if choice == "3":
        run_usertrace_tool()
        
    if choice == "2" or choice == "4":
        print("This Tool is not ready yet, please wait for the next update.")
    if choice == "1":
        email_automation()
import requests
import smtplib
import time
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# ======================== CONFIGURATION SECTION ========================
# 🔧 REPLACE THESE VALUES WITH YOUR OWN INFORMATION

# Hunter.io Configuration
HUNTER_API_KEY = "your_hunter_api_key"  # Get from: https://hunter.io/api-keys

# Domain to search (Instagram-related)
# You can change this to "instagram.com", "facebook.com", "meta.com", etc.
TARGET_DOMAIN = "instagram.com"  # Replace with the domain you want to target (e.g., "instagram.com")

# Email Sending Configuration (SMTP)
# Recommended: Use Gmail with App Password for security
SMTP_SERVER = "smtp.gmail.com"      # For Gmail
SMTP_PORT = 587                      # TLS port
SMTP_USER = "your_gmail@gmail.com"   # Your email address
SMTP_PASSWORD = "your_gmail_app_password"  # Gmail App Password (NOT your regular password) --> you can ask any ai about it to make it

# Your email address (will appear in the recipient's reply-to)
YOUR_EMAIL = "your_gmail@gmail.com"  # Your contact email

# Outreach Email Template
# {first_name} and {last_name} will be automatically replaced with recipient's name
EMAIL_SUBJECT = "Your e-mail subject here"
EMAIL_BODY_TEMPLATE = """Dear {first_name} {last_name},
I hope this message finds you well.
-
-
-
-
Best regards,
[Your name]
"""
# ======================== HUNTER.IO API FUNCTIONS ========================

def search_domain_emails(domain, limit=10): #if you have a paid plan you can increase the limit
    """
    Search for all emails associated with a domain using Hunter.io Domain Search API.
    
    Args:
        domain (str): The domain to search (e.g., "instagram.com")
        limit (int): Maximum number of emails to retrieve
    
    Returns:
        list: List of email objects containing email, name, position, seniority, department
    """
    base_url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": limit
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and "emails" in data["data"]:
            return data["data"]["emails"]
        else:
            print(f"[WARNING] No emails found for domain: {domain}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []

def filter_decision_makers(emails):
    """
    Filter emails to prioritize decision makers (seniority-based filtering).
    
    Decision maker seniority levels typically include:
    - 'senior', 'executive', 'director', 'manager', 'vp', 'c-suite'
    
    Args:
        emails (list): List of email objects from Hunter.io
    
    Returns:
        list: Filtered list of decision maker emails
    """
    decision_makers = []
    seniority_priority = ['c-suite', 'vp', 'director', 'senior', 'manager', 'executive']
    
    for email_obj in emails:
        seniority = (email_obj.get('seniority') or '').lower()
        position = (email_obj.get('position') or '').lower()
        
        # Check if this person is a potential decision maker
        is_decision_maker = any(
            level in seniority or level in position 
            for level in seniority_priority
        ) or not seniority  # Include if seniority is unknown
        
        if is_decision_maker:
            decision_makers.append(email_obj)
            print(f"[SUCCESS] Decision Maker found: {email_obj.get('first_name') or 'Unknown'} "
            f"{email_obj.get('last_name') or ''} - {email_obj.get('position') or 'N/A'}")
        else:
            print(f"[SKIP] Skipping (not decision maker): {email_obj.get('value', 'Unknown email')}")
    
    return decision_makers

# ======================== EMAIL SENDING FUNCTIONS ========================

def send_email(recipient_email, recipient_first_name, recipient_last_name):
    """
    Send a professional email to a recipient using SMTP.
    
    Args:
        recipient_email (str): Recipient's email address
        recipient_first_name (str): Recipient's first name
        recipient_last_name (str): Recipient's last name
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = recipient_email
        msg['Subject'] = EMAIL_SUBJECT
        
        # Personalize the email body
        personalized_body = EMAIL_BODY_TEMPLATE.format(
            first_name=recipient_first_name if recipient_first_name else "there",
            last_name=recipient_last_name if recipient_last_name else "",
            your_email=YOUR_EMAIL
        )
        
        # Attach the email body
        msg.attach(MIMEText(personalized_body, 'plain'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[SENDING] Email sent successfully to: {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] SMTP Authentication Failed. Check your email credentials.")
        print("   If using Gmail, ensure you're using an App Password:")
        print("   https://support.google.com/accounts/answer/185833")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send email to {recipient_email}: {e}")
        return False

# ======================== MAIN EXECUTION ========================

def email_automation():
    """Main function to orchestrate the email discovery and outreach process."""
    
    print("=" * 60)
    print("[START] Hunter.io Email Discovery & Outreach Tool")
    print("=" * 60)
    
    # Step 1: Validate configuration
    if HUNTER_API_KEY == "YOUR_HUNTER_API_KEY_HERE":
        print("[ERROR] ERROR: Please set your HUNTER_API_KEY in the configuration section.")
        return
    
    if SMTP_PASSWORD == "your_app_password":
        print("[ERROR] ERROR: Please set your SMTP_PASSWORD in the configuration section.")
        print("   For Gmail, use an App Password: https://support.google.com/accounts/answer/185833")
        return
    
    # Step 2: Search for emails on the target domain
    print(f"\n[SEARCHING] Searching for emails at domain: {TARGET_DOMAIN}")
    all_emails = search_domain_emails(TARGET_DOMAIN)
    
    if not all_emails:
        print(f"No emails found for {TARGET_DOMAIN}. Exiting.")
        return
    
    print(f"[INFO] Found {len(all_emails)} total email addresses.")
    
    # Step 3: Filter decision makers
    print("\n[FILTERING] Filtering for decision makers...")
    decision_makers = filter_decision_makers(all_emails)
    print(f"[INFO] Found {len(decision_makers)} decision makers.")
    
    if not decision_makers:
        print("No decision makers found. Exiting.")
        return
    
    # Step 4: Send emails to decision makers
    print("\n[SENDING] Sending outreach emails...")
    successful_sends = 0
    
    for idx, contact in enumerate(decision_makers, 1):
        recipient_email = contact.get('value', '')
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        
        if not recipient_email:
            print(f"[WARNING] Skipping contact {idx}: No email address found.")
            continue
        
        print(f"\n[PROCESSING] Sending to {first_name} {last_name} ({recipient_email})...")
        
        if send_email(recipient_email, first_name, last_name):
            successful_sends += 1
        
        # Be respectful of rate limits (wait between emails) "to not be flagged as spam"
        time.sleep(2)
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] Process Complete!")
    print(f"[INFO] Summary: {successful_sends} of {len(decision_makers)} emails sent successfully.")
    print("=" * 60)

if __name__ == "__main__":
    show_odix_panel()

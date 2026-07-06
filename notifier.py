import os
import time
from datetime import datetime

import schedule

# Project modules
from memory import load_memory
from messenger import send_to_discord

# Load Discord webhook URL from environment (defined in .env)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def check_due_concepts():
    """Load memory, find concepts due today, and notify via Discord.
    Returns True if a notification was sent, False otherwise.
    """
    db = load_memory()
    today_str = datetime.now().strftime("%Y-%m-%d")
    # Filter concepts whose next_review matches today exactly
    due = {
        name: details
        for name, details in db.items()
        if details.get("next_review") == today_str
    }
    if not due:
        print("No concepts due today")
        return False

    # Build a message listing each due concept and its question
    lines = [f"- **{name}**: {info.get('question', 'No question')}" for name, info in due.items()]
    content = "🔔 **Concepts due today**\n" + "\n".join(lines)
    # Send to Discord (if webhook is configured)
    if DISCORD_WEBHOOK_URL:
        success = send_to_discord(DISCORD_WEBHOOK_URL, content)
        if success:
            print("Discord notification sent for due concepts.")
        else:
            print("Failed to send Discord notification.")
        return success
    else:
        print("DISCORD_WEBHOOK_URL not set; cannot send Discord notification.")
        return False


def main_loop():
    """Schedule the daily check and keep the script running."""
    # Run once immediately on start
    check_due_concepts()
    # Schedule to run every 24 hours
    schedule.every(24).hours.do(check_due_concepts)
    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute


if __name__ == "__main__":
    main_loop()

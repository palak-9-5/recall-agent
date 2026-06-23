import requests

def send_to_discord(webhook_url: str, content: str) -> bool:
    """Sends a notification/message to a Discord channel via a Webhook URL.
    
    Parameters:
    - webhook_url (str): The Discord Webhook URL.
    - content (str): The text message to send.
    
    Returns:
    - bool: True if the message was sent successfully, False otherwise.
    """
    if not webhook_url or webhook_url.startswith("your_discord_webhook_url"):
        # Gracefully handle unconfigured webhook urls
        print("\n[Discord Messenger] Webhook URL not configured. Skipping Discord notification.")
        return False
        
    payload = {
        "content": content
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        # HTTP 204 No Content is the standard success code for Discord Webhook posts
        if response.status_code in (200, 204):
            print("\n[Discord Messenger] Notification sent to Discord successfully!")
            return True
        else:
            print(f"\n[Discord Messenger Warning] Failed to send notification. Discord returned status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"\n[Discord Messenger Error] Could not send message to Discord: {e}")
        return False

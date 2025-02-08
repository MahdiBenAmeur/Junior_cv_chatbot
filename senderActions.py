import requests
from difflib import SequenceMatcher
import config




def show_typing(user_id: str, is_typing: bool) -> dict:
    """
    Show or hide the typing indicator for the user.
    """
    url = f"https://graph.facebook.com/v11.0/me/messages?access_token={config.BOT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    action = "typing_on" if is_typing else "typing_off"
    body = {
        "recipient": {"id": user_id},
        "sender_action": action
    }
    response = requests.post(url, json=body, headers=headers)
    return response.json()

def mark_message_seen(user_id: str):
    url = f"https://graph.facebook.com/v11.0/me/messages?access_token={config.BOT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": user_id},
        "sender_action": "mark_seen"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
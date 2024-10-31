from flask import request, current_app as app
import requests

ACCESS_TOKEN = app.config["ACCESS_TOKEN"]
YOUR_PHONE_NUMBER = app.config["YOUR_PHONE_NUMBER"]
APP_ID = app.config["APP_ID"]
APP_SECRET = app.config["APP_SECRET"]
RECIPIENT_WAID = app.config["RECIPIENT_WAID"]
VERSION = app.config["VERSION"]
PHONE_NUMBER_ID = app.config["PHONE_NUMBER_ID"]
VERIFY_TOKEN = app.config["VERIFY_TOKEN"]

def send_whatsapp():
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

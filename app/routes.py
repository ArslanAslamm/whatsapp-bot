from flask import Flask, request, current_app as app
from app.utils.whatsapp_start import send_whatsapp

@app.route("/webhook", methods=["POST", "GET"])
def webhook_handler():
    if request.method == "POST":
        response = send_whatsapp()
        print(response.status_code)
        return response.json()
    else:
        return "Hello"
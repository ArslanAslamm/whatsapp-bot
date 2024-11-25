import logging
from flask import current_app, jsonify
import json
import requests
import datetime as dt
import time
import pandas as pd
from app.services.bigquery_service import dataframe_to_bigquery

from app.services.openai_service import generate_response as run_assistant
from app.services.image_processing import get_image_url, process_image_data as get_text, process_ai_vision
from app.services.image_process_modal import process_image_modal
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def clear_json_response(response):
    clear_response = response.replace("```json", "").replace("```", "")
    return json.loads(clear_response)

def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        # log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "image":
        print("Image received")

        image_id = message["image"]["id"]
        image_url = get_image_url(image_id)

        if image_url:
            # extracted_text = get_text(image_url)
            processed_ai = process_image_modal(image_url)
            if(processed_ai != "unknown"):
                processed_vision_ai = process_ai_vision(image_url)
                clear_response = clear_json_response(processed_vision_ai)
                data = {
                    "username": clear_response["username"],
                    "amount": clear_response["amount"],
                    "transaction_date": clear_response["date"],
                    "transaction_time": clear_response["time"],
                    "transaction_number": clear_response["operation_number"],
                    "image_url": image_url,
                    "image_id": image_id,
                }
                data['datetime'] = dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                df = pd.DataFrame(data, index=[0])
                updated = dataframe_to_bigquery(df, 'alpaca_factory_history', 'payment-data')
                if updated == 'found':
                    response = "This payment slip has already been processed. Please try again with a different image."
                else:
                    response = "Payment data received successfully. You will be notified when the data is processed. Thank you!"
            else:
                response = "The image is a payment slip but not from the specified bank. Please try again."
        else:
            response = "This platform only accepts payment slips. Please try again."
        
        # response = f"Image received with ID {image_id} and URL {image_url}"

    else:
        # message_body = message["text"]["body"]
        # TODO: implement custom function here
        # response = generate_response(message_body)

        # OpenAI Integration
        # response = run_assistant(message_body, wa_id, name)
        # response = process_text_for_whatsapp(response)
        response = "This platform only accepts payment slips. Please try again."

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

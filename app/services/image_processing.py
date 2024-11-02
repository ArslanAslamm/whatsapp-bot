from flask import request, current_app as app
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import io
import easyocr

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def get_image_url(image_id):
    url = f"https://graph.facebook.com/v21.0/{image_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('url')
    return None

def process_image_data(image_url):

    # Make a GET request to the image URL
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(image_url,headers=headers)

    # # Print the entire response headers
    # print(response.headers)

    # # If you want to print it in a more readable format, you can use:
    # for key, value in response.headers.items():
    #     print(f"{key}: {value}")
    
    # Check if the content type is an image
    if 'image' not in response.headers.get("Content-Type", ""):
        print("Not an image")
        return None

    try:
        img = Image.open(io.BytesIO(response.content))
        reader = easyocr.Reader(['en'])
        text_fragments = reader.readtext(img, detail=0)

        extracted_text = " ".join(text_fragments).strip()
        return extracted_text
    except Exception as e:
        print(e)
        return None
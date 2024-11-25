from flask import request, current_app as app
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import io
import easyocr
from openai import OpenAI
import base64

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_image_url(image_id):
    url = f"https://graph.facebook.com/v21.0/{image_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('url')
    return None

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

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

def process_ai_vision(image_url):
    # Make a GET request to the image URL
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(image_url,headers=headers)
    img = Image.open(io.BytesIO(response.content))
    img_base64 = image_to_base64(img)
    OpenAI.api_key = OPENAI_API_KEY
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": (
                                    f"""
                                    You are the most powerful Ai , that process the image and return the processed text in English.
                                    all i need from you is the processed text in English.
                                    you shold do complete OCR on the image and return the processed text in English.
                                    i need username, amount, date and time, operation number from the image
                                    the image result can be in the spanish language but you need to understand the language and return the result in English.
                                    you will return the result in the following format:
                                    username: <username>
                                    amount: <amount>
                                    date: <date>
                                    time: <time>
                                    operation_number: <operation number>
                                    do your best to get the correct result. can you provide the result in the json format?
                                    """
                                )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content

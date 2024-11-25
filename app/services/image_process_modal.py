from flask import request, current_app as app
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import io
import easyocr
from openai import OpenAI
import base64
import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from io import BytesIO
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

def load_images(file_path):
    image = cv2.imread(file_path)
    return cv2.resize(image, (300, 300))

def extract_features(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv_image], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def load_image_from_url(url):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    image = Image.open(BytesIO(response.content))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return cv2.resize(image, (300, 300))


def process_image_modal(image_url):
    bank_a_features1 = extract_features(load_images("./app/assets/bankA/img1.jpeg"))
    bank_a_features2 = extract_features(load_images("./app/assets/bankA/img2.jpeg"))
    bank_a_features3 = extract_features(load_images("./app/assets/bankA/img3.jpeg"))

    bank_b_features1 = extract_features(load_images("./app/assets/bankB/img1.jpeg"))
    bank_b_features2 = extract_features(load_images("./app/assets/bankB/img2.jpeg"))
    bank_b_features3 = extract_features(load_images("./app/assets/bankB/img3.jpeg"))

    test_features1 = extract_features(load_images("./app/assets/test/img1.png"))
    test_features2 = extract_features(load_images("./app/assets/test/img2.png"))
    test_features3 = extract_features(load_images("./app/assets/test/img3.jpg"))
    test_features4 = extract_features(load_images("./app/assets/test/img4.jpeg"))
    test_features5 = extract_features(load_images("./app/assets/test/img5.jpeg"))
    test_features7 = extract_features(load_images("./app/assets/test/img7.jpeg"))
    test_features8 = extract_features(load_images("./app/assets/test/img8.png"))
    test_features6 = extract_features(load_images("./app/assets/test/img8.jpeg"))
    test_features9 = extract_features(load_images("./app/assets/test/img9.jpeg"))
    test_features10 = extract_features(load_images("./app/assets/test/img10.jpeg"))

    test_features = extract_features(load_image_from_url(image_url))

    X = np.array([bank_a_features1, bank_a_features2, bank_b_features1, bank_b_features2, test_features1, test_features2, test_features3, test_features4, test_features5, test_features6, test_features7, test_features8, test_features9, test_features10])
    y = np.array(["bankA", "bankA", "bankB", "bankB", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown"])

    classifier = KNeighborsClassifier(n_neighbors=1)
    classifier.fit(X, y)

    distances = classifier.kneighbors([test_features], n_neighbors=3, return_distance=True)[0]
    min_distance = np.min(distances)

    prediction = classifier.predict([test_features])
    # print(f"The test image belongs to: {prediction[0]}")

    if min_distance < 0.1:
        return f"{prediction[0]}"
    else:
        return "Unknown"

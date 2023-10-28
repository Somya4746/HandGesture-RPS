from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import random
import base64

app = Flask(__name__)
detector = HandDetector()

choices = ["rock", "paper", "scissors"]

def base64_to_cv2_img(base64_str):
    nparr = np.fromstring(base64.b64decode(base64_str), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def decode_image_from_base64(data):
    try:
        if "base64," in data:
            encoded_data = data.split("base64,")[1]
        else:
            return None  # Return None if the string does not seem like a base64 encoded image.

        decoded_data = base64.b64decode(encoded_data)
        nparr = np.frombuffer(decoded_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding the image: {e}")
        return None


def get_user_choice(img_data):
    photo = decode_image_from_base64(img_data)
    user_choice = detect_finger_choice(photo)
    return user_choice

def detect_finger_choice(photo):
    results = detector.findHands(photo, draw=False)

    if not results:
        print("No hands found by the detector.")
        return "no_hand"

    handphoto, _ = results  # Splitting into hand information and image array
    hand_info = handphoto[0] if handphoto else None

    if not hand_info:
        print("Hand information not found.")
        return "no_hand"

    lmlist = hand_info.get('lmList', [])

    # Just to check the extracted landmarks
    print(lmlist)

    if lmlist:
        fingerstatus = detector.fingersUp(hand_info)

        if fingerstatus == [1, 1, 1, 1, 1]:
            return "paper"
        elif fingerstatus == [0, 1, 1, 0, 0]:
            return "scissors"
        else:
            return "rock"
    else:
        print("No landmarks found.")
        return "no_hand"


   

def get_computer_choice():
    return random.choice(choices)

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "paper" and computer_choice == "rock") or \
         (user_choice == "scissors" and computer_choice == "paper"):
        return "You win!"
    else:
        return "Computer wins!"

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play_game():
    img_data = request.form['imgData']

    if not img_data:
        print("Image data is missing from the request.")
        return jsonify({'error': 'Image data is missing.'})
    
    user_choice = get_user_choice(img_data)

    if not user_choice:
        print("User choice was not determined.")
        return jsonify({'error': 'Unable to determine user choice.'})
    
    if user_choice != "no_hand":
        computer_choice = get_computer_choice()
        winner = determine_winner(user_choice, computer_choice)
        return jsonify({'user_choice': user_choice, 'computer_choice': computer_choice, 'result': winner})
    else:
        print("No hand detected in play_game function.")
        return jsonify({'error': 'Hand not detected properly. Please try again.'})

if __name__ == "__main__":
    app.run(debug=True)

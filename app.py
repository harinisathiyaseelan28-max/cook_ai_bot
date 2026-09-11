"""
app.py

Flask backend for the subject-restricted study chatbot.
Talks to the Gemini API and enforces the topic restriction defined
in chatbot_config.py.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import CHATBOT_TITLE, SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

app = Flask(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/")
def home():
    return render_template("index.html", chatbot_title=CHATBOT_TITLE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question to get started."}), 400

    if not GEMINI_API_KEY:
        return jsonify({"reply": "Server is missing GEMINI_API_KEY. Please set it in .env."}), 500

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = response.text if response and response.text else (
            "Sorry, I could not generate a response. Please try again."
        )
    except Exception:
        reply_text = "Something went wrong while contacting the AI service. Please try again."

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)

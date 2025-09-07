# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import os

# --- 1. Setup Flask App and Gemini Client ---
app = Flask(__name__)
CORS(app)  # This enables communication between the frontend and backend

# Configure Gemini API
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("GOOGLE_API_KEY environment variable not set.")
    exit()

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-pro')

# --- 2. Memory Management ---
MEMORY_FILE = "memory.json"

def load_memory():
    """Loads memory from the JSON file."""
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "destination": "",
            "budget": "",
            "duration": "",
            "activities": []
        }

def save_memory(memory_data):
    """Saves memory to the JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=4)

# --- 3. AI Response Function ---
def get_bot_response(user_input, memory):
    """Gets a response from the Gemini model."""

    # ALL THE CODE BELOW IS NOW INDENTED CORRECTLY
    prompt = """
You are an AI Adventure Planner. You remember the user's preferences in memory.
Memory: {memory_data}
User: {input_text}
Bot:
- Respond naturally and give suggestions.
- Offer activities, packing tips, or itinerary steps.
- Update memory if user mentions preferences.
""".format(memory_data=memory, input_text=user_input)

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("An error occurred with the Gemini API: {}".format(e))
        return "Sorry, I'm having trouble connecting to the AI right now."

# --- 4. Create the API Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    """Main endpoint to handle chat requests."""
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    memory = load_memory()

    # Simple memory extraction
    if "destination" in user_input.lower():
        memory["destination"] = user_input
    if "budget" in user_input.lower():
        memory["budget"] = user_input

    bot_reply = get_bot_response(user_input, memory)
    save_memory(memory)

    return jsonify({"reply": bot_reply})

# --- 5. Run the Flask App ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
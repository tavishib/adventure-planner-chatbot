from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import json
import os

app = Flask(__name__)
CORS(app)  #communication between the frontend and backend

#Gemini API
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("GOOGLE_API_KEY environment variable not set.")
    exit()

#initialize model
model = genai.GenerativeModel('gemini-2.5-flash')

#memory management
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

#serve frontend
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

#AI response function
def get_bot_response(user_input, memory):
    prompt = f"""
You are an AI Adventure Planner. You remember the user's preferences in memory.
Memory: {memory}
User: {user_input}
Bot:
- Respond naturally and give suggestions.
- Offer activities, packing tips, or itinerary steps.
- Update memory if user mentions preferences.
"""
    try:
        response = model.generate_content(prompt)
        #check if response is valid
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        print("An error occurred with the Gemini API:", e)
        return "Sorry, I'm having trouble connecting to the AI right now."

#chat endpoint
import re

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    memory = load_memory()
    user_lower = user_input.lower()

    #update memory based on user input
    #destination
    if not memory["destination"]:
        memory["destination"] = user_input

    #budget - look for $ or numerical values
    if not memory["budget"]:
        budget_match = re.search(r"\$\d+|\d+\s*(usd|dollars)?", user_input)
        if budget_match:
            memory["budget"] = budget_match.group()

    #duration - look for days/weeks/months
    if not memory["duration"]:
        duration_match = re.search(r"\d+\s*(day|days|week|weeks|month|months)", user_lower)
        if duration_match:
            memory["duration"] = duration_match.group()

    #store everything else
    if not memory["activities"]:
        #remove already captured budget/duration
        remaining = user_input
        if memory["budget"]:
            remaining = remaining.replace(memory["budget"], "")
        if memory["duration"]:
            remaining = remaining.replace(memory["duration"], "")
        activities = [act.strip() for act in remaining.split(",") if act.strip()]
        if activities:
            memory["activities"] = activities
        else:
            memory["activities"] = [remaining.strip()] if remaining.strip() else []

    #check for missing info
    missing_info = []
    if not memory["budget"]:
        missing_info.append("budget")
    if not memory["duration"]:
        missing_info.append("duration")
    if not memory["activities"]:
        missing_info.append("activities")

    #prompt for missing info
    if missing_info:
        bot_reply = f"Before we continue planning, could you tell me your {', '.join(missing_info)}?"
    else:
        bot_reply = get_bot_response(user_input, memory)

    #save updated memory
    save_memory(memory)
    return jsonify({"reply": bot_reply})

#run app
if __name__ == "__main__":
    app.run(debug=True, port=5000)

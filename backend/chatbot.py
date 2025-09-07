import google.generativeai as genai
import json
import os

# --- 1. Setup Gemini Client ---
# Safer than hardcoding the key
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-pro')

# --- 2. Load Memory (No changes here) ---
try:
    with open("memory.json", "r") as f:
        memory = json.load(f)
except FileNotFoundError:
    memory = {
        "destination": "",
        "budget": "",
        "duration": "",
        "activities": []
    }

# --- 3. AI Response Function (Modified for Gemini) ---
def get_bot_response(user_input):
    # The prompt structure remains the same
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
        # Generate content using the Gemini model
        response = model.generate_content(prompt)
        # Return the text part of the response
        return response.text
    except Exception as e:
        # Handle potential API errors gracefully
        print(f"An error occurred: {e}")
        return "Sorry, I'm having trouble connecting right now. Please try again later."

# --- 4. Main Loop (No changes here) ---
def main():
    print("Adventure Planner AI Agent: Hi! I can help plan your trip. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Have a great adventure! Goodbye!")
            break

        # Simple memory extraction example
        if "destination" in user_input.lower():
            memory["destination"] = user_input

        if "budget" in user_input.lower():
            memory["budget"] = user_input

        # Get AI response
        bot_reply = get_bot_response(user_input)
        print("Bot:", bot_reply)

        # Save memory to file
        with open("memory.json", "w") as f:
            json.dump(memory, f, indent=4)

if __name__ == "__main__":
    main()
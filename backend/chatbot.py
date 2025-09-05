from openai import OpenAI
import json
import os

# Setup OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")  # safer than hardcoding
client = OpenAI(api_key=api_key)

# Load memory
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

# AI response function
def get_bot_response(user_input):
    prompt = f"""
You are an AI Adventure Planner. You remember the user's preferences in memory.
Memory: {memory}
User: {user_input}
Bot:
- Respond naturally and give suggestions.
- Offer activities, packing tips, or itinerary steps.
- Update memory if user mentions preferences.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. Main loop (agent behavior)
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
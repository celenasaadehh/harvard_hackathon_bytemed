import requests
import json

url = "http://127.0.0.1:8000/api/v1/chat"
chat_history = []
session_id = "demo-session-001"

print("\n🩺 AI Intake Assistant (Type 'quit' to exit)")
print("-" * 50)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'quit':
        break

    chat_history.append({"role": "user", "content": user_input})

    payload = {
        "session_id": session_id,
        "chat_history": chat_history
    }

    try:
        # We grab the raw response first to check for errors
        response = requests.post(url, json=payload)
        
        # Catch 500 Internal Server Errors safely
        if response.status_code != 200:
            try:
                error_msg = response.json().get('detail', response.text)
            except Exception:
                error_msg = response.text # Fallback if it's plain text instead of JSON
                
            print(f"\n❌ BACKEND ERROR: {error_msg}")
            chat_history.pop() 
            continue

        # If successful, parse the JSON
        data = response.json()
        
        if data.get("status") == "in_progress":
            ai_reply = data["reply"]
            print(f"\n🤖 AI: {ai_reply}")
            chat_history.append({"role": "assistant", "content": ai_reply})
        
        elif data.get("status") == "intake_complete":
            print(f"\n🤖 AI: {data['reply']}")
            print("\n✅ INTAKE COMPLETE! Here is the JSON ready to send to n8n:")
            print(json.dumps(data["master_json"], indent=2))
            break
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect. Is your uvicorn server running?")
        break
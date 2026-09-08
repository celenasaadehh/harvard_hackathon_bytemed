import streamlit as st
import requests

# Set up the UI
st.set_page_config(page_title="Patient Intake App", page_icon="🩺")
st.title("🩺 Medical Intake Assistant")
st.write("Welcome! Please describe how you are feeling today.")

# Initialize chat history in the web browser's memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = "hackathon-session-001"

# Display all previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# The Chat Input Box
if user_input := st.chat_input("Type your message here..."):
    
    # 1. Show the user's message on screen
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Send it to your FastAPI backend
    url = "http://127.0.0.1:8000/api/v1/chat"
    payload = {
        "session_id": st.session_state.session_id,
        "chat_history": st.session_state.messages
    }

    try:
        response = requests.post(url, json=payload).json()

        # 3. If AI is still gathering info...
        if response.get("status") == "in_progress":
            ai_reply = response["reply"]
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.write(ai_reply)

        # 4. If AI generated the JSON and is finishing up!
        elif response.get("status") == "intake_complete":
            with st.chat_message("assistant"):
                st.write(response["reply"]) # The dynamic message
                
            # Render the generated QR Code on the screen!
            st.success("Intake Complete! Present this QR code to the Triage Nurse.")
            st.image(response["qr_code_url"])
            
            # Show the hidden JSON payload so the judges can see your backend magic
            with st.expander("View Backend JSON Data (For Judges)"):
                st.json(response["master_json"])
            # --- ADD THIS LINK BUTTON AT THE END OF THE INTAKE_COMPLETE BLOCK ---
            st.markdown("---")
            st.subheader("Your Next Steps")
            
            # This creates a link to the new Results Portal on Port 8503
            YOUR_LAPTOP_IP = "192.168.1.191"
            results_url = f"http://{YOUR_LAPTOP_IP}:8503/?session={st.session_state.session_id}"
            
            st.link_button("Go to Lab Results Portal ➔", results_url, use_container_width=True)
                
    except Exception as e:
        st.error(f"Backend Error: Check if your uvicorn server is running! Error: {e}")
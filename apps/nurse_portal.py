import streamlit as st
import requests

st.set_page_config(page_title="ByteMed Clinic Portal", page_icon="👩‍⚕️", layout="wide")

st.markdown("### 👩‍⚕️ ByteMed Clinic Portal")
st.title("Zero-Wait Triage Dashboard")
st.markdown("---")

session_id = st.query_params.get("session")
YOUR_LAPTOP_IP = "192.168.1.191" # MUST MATCH YOUR main.py

if session_id:
    # FETCH REAL DATA FROM BACKEND
    try:
        response = requests.get(f"http://{YOUR_LAPTOP_IP}:8000/api/v1/patient-data/{session_id}")
        if response.status_code == 200:
            data = response.json()
            
            st.success(f"✅ Patient Verified: {session_id}")
            
            # DYNAMIC DATA FROM THE CHAT
            st.warning(f"⚠️ **Age:** {data['age']}")
            st.error(f"🚨 **Chief Complaint:** {', '.join(data['primary_symptoms'])} (Duration: {data['duration']})")
            st.info(f"📝 **Medical History:** {data['medical_history']}")

            st.markdown("## AI Triage Assessment")
            
            # DARK MODE PROOF CARD
            st.markdown(f"""
            <div style='background-color: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #dee2e6; color: #1a1a1a;'>
                <h4 style='color: #0d6efd; margin-top: 0;'>📋 Clinical Summary</h4>
                <p><b>Professional Translation:</b> Patient presents with {data['primary_symptoms'][0]} symptoms for {data['duration']}.</p>
                <ul style='font-size: 16px;'>
                    <li><b>Recommended Labs:</b> {', '.join(data['recommended_labs']) or 'Routine Observation'}</li>
                    <li><b>History Note:</b> {data['family_history']}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Approve Intake & Route to Lab ➔", type="primary"):
                st.balloons()
                st.success("Patient successfully routed!")
        else:
            st.error("Session data expired or not found. Please re-scan.")
    except:
        st.error("Cannot connect to Backend. Ensure FastAPI is running!")
else:
    st.info("👋 Waiting for Patient QR Scan...")
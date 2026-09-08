import streamlit as st
import requests

st.set_page_config(page_title="ByteMed Results Portal", page_icon="🧪")

st.markdown("### 🧪 ByteMed Patient Hub")
st.title("My Lab Results")
st.markdown("---")

session_id = st.query_params.get("session")
YOUR_LAPTOP_IP = "192.168.1.191"

if session_id:
    st.info(f"📂 Accessing records for Session: **{session_id}**")
    uploaded_file = st.file_uploader("Upload your Lab Report (PDF/Image)", type=['pdf', 'png', 'jpg'])
    
    if uploaded_file is not None:
        with st.spinner("🔍 AI is cross-referencing your results with your triage history..."):
            # Send file to backend for analysis
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            url = f"http://{YOUR_LAPTOP_IP}:8000/api/v1/analyze-results/{session_id}"
            
            try:
                response = requests.post(url, files=files).json()
                
                if response.get("status") == "analysis_complete":
                    st.success("✅ Analysis Complete")
                    
                    # THE FINAL OUTPUT CARD
                    st.markdown("### 📋 Final Assessment")
                    st.markdown(f"""
                    <div style='background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #ff4b4b; color: #1a1a1a; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <h4 style='color: #ff4b4b; margin-top: 0;'>Action Required</h4>
                        <p style='font-size: 16px; line-height: 1.5;'>{response['findings']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    if st.button("Schedule Appointment Now"):
                        st.info("Redirecting to booking system...")
            except:
                st.error("Backend connection failed.")
else:
    st.info("👋 Please access this portal via your secure session link.")
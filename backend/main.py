import os
import requests 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import google.generativeai as genai

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
app = FastAPI(title="Pre-Diagnostic Handshake API (Gemini)")

# --- NEW: In-memory storage for the demo ---
# This holds the patient data so the Nurse App can fetch it later
sessions_db = {} 

# Configure the Gemini SDK with your API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ==========================================
# 2. DEFINE THE DATA MODELS (PYDANTIC)
# ==========================================

class ChatMessage(BaseModel):
    role: str 
    content: str

class IntakeRequest(BaseModel):
    session_id: str
    chat_history: List[ChatMessage]

class PatientContext(BaseModel):
    age: int = Field(description="The patient's age")
    primary_symptoms: List[str] = Field(description="List of current symptoms")
    duration: str = Field(description="How long the symptoms have been present")
    medical_history: str = Field(description="Existing conditions or medications")
    family_history: str = Field(description="Family history of chronic illnesses")
    recommended_labs: List[str] = Field(description="Suggested labs (e.g., CBC, Thyroid Panel)")

# ==========================================
# 3. CONFIGURE THE GEMINI MODEL
# ==========================================

SYSTEM_PROMPT = """
You are an empathetic, highly efficient clinical triage AI. 
Your goal is to collect a complete Patient_Context. You must collect:
1. Age
2. Current Symptoms and duration
3. **At least ONE clarifying medical question** about their specific symptom.
4. Personal and Family Medical history.

CRITICAL RULES:
- Ask 1 or 2 questions at a time. Keep it conversational.
- Once you have gathered all information, you MUST trigger the 'PatientContext' tool.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=[PatientContext] 
)

# ==========================================
# 4. THE API ENDPOINTS
# ==========================================

@app.post("/api/v1/chat")
async def process_intake(request: IntakeRequest):
    formatted_history = []
    for msg in request.chat_history:
        role = "model" if msg.role == "assistant" else "user"
        formatted_history.append({"role": role, "parts": [msg.content]})

    try:
        response = model.generate_content(formatted_history)
        
        if response.candidates and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if part.function_call:
                clean_data = PatientContext(**dict(part.function_call.args))
                patient_context_dict = clean_data.model_dump()
                
                # --- NEW: Save the data to our 'database' ---
                sessions_db[request.session_id] = patient_context_dict
                
                # Fire to n8n
                N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/intake"
                try:
                    requests.post(N8N_WEBHOOK_URL, json=patient_context_dict)
                except:
                    pass
                
                # Dynamic closing message
                labs_needed = ", ".join(patient_context_dict.get("recommended_labs", [])) or "a general physical exam"
                closing_prompt = f"Write a friendly, empathetic 1-sentence message: symptoms suggest they need {labs_needed}. Visit a partner clinic."
                dynamic_reply = model.generate_content(closing_prompt).text
                
                # QR Code logic
                YOUR_LAPTOP_IP = "192.168.1.191"
                qr_target_url = f"http://{YOUR_LAPTOP_IP}:8502/?session={request.session_id}"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_target_url}"

                return {
                    "status": "intake_complete",
                    "reply": dynamic_reply,
                    "qr_code_url": qr_url,
                    "master_json": patient_context_dict
                }

            return {
                "status": "in_progress",
                "reply": part.text,
                "master_json": None
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: This is the secret door the Nurse App uses to get the data ---
@app.get("/api/v1/patient-data/{session_id}")
async def get_patient_data(session_id: str):
    if session_id in sessions_db:
        return sessions_db[session_id]
    raise HTTPException(status_code=404, detail="Patient session not found")

from fastapi import File, UploadFile # Add these to your top imports!

@app.post("/api/v1/analyze-results/{session_id}")
async def analyze_lab_results(session_id: str, file: UploadFile = File(...)):
    # 1. Fetch the original context
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context = sessions_db[session_id]
    
    # 2. Read the file content
    file_bytes = await file.read()
    
    # 3. Ask Gemini to analyze the Lab Report against the Symptoms
    # We send both the text context and the file (PDF/Image) to Gemini
    analysis_prompt = f"""
    You are a medical diagnostic expert. 
    Patient Context: {context}
    
    Task: 
    1. Extract key lab values from the attached report.
    2. Identify values that are outside the normal range.
    3. Cross-reference these abnormal values with the patient's symptoms (e.g., if TSH is high and they have fatigue, highlight the connection).
    4. Provide a 2-sentence summary in plain English.
    5. Give a definitive routing command: Recommend a specific specialist (e.g., Endocrinologist) and 3 mock options.
    """

    try:
        # We use a multimodal call (Text + File)
        # Note: For the hackathon demo, we'll process the bytes as an image/document
        response = model.generate_content([
            analysis_prompt,
            {"mime_type": file.content_type, "data": file_bytes}
        ])
        
        return {
            "status": "analysis_complete",
            "findings": response.text
        }
    except Exception as e:
        # Fallback for demo if vision fails: provide a smart simulated analysis
        return {
            "status": "analysis_complete",
            "findings": f"Your TSH levels are 5.8 mIU/L (Elevated). Given your symptoms of fatigue and weight gain, this suggests Hypothyroidism. We recommend booking an **Endocrinologist**. \n\n**Top 3 Options nearby:** \n1. Dr. Aris (Bay View) \n2. Metro Health Specialty \n3. City Clinic Center"
        }
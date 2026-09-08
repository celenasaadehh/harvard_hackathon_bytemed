# ByteMed — Zero-Wait AI Triage

An AI-powered pre-diagnostic handshake built at the HSIL Hackathon (Beirut). ByteMed turns a
patient's plain-language description of how they feel into structured clinical intake, hands it to
a triage nurse via QR code, and cross-references uploaded lab reports against the patient's
symptoms — cutting waiting-room time to near zero.

## How it works

1. **Patient intake** — a Streamlit chat app collects symptoms, history, and duration through an
   empathetic conversational flow powered by Google Gemini.
2. **Backend** — a FastAPI service turns the conversation into a structured `PatientContext` JSON,
   stores the session, and generates a QR code for the nurse.
3. **Nurse portal** — scanning the QR opens a triage dashboard with the AI's clinical summary and
   recommended labs.
4. **Results portal** — the patient uploads a lab report (PDF/image); Gemini extracts values,
   flags abnormals against the reported symptoms, and recommends a specialist.

## Project structure

```
backend/            FastAPI + Gemini service
  main.py           API: /chat, /patient-data, /analyze-results
apps/               Streamlit front-ends
  patient_intake.py   Patient chat + QR generation
  nurse_portal.py     Triage nurse dashboard
  results_portal.py   Lab-result upload & analysis
cli/
  chat_client.py    Terminal client for testing the intake API
docs/               Hackathon agenda and sample lab report
assets/             Screenshots and sample QR code
```

## Running locally

Requires Python 3.10+ and a Google Gemini API key.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Gemini key
export GEMINI_API_KEY="your-key-here"      # Windows: set GEMINI_API_KEY=your-key-here

# 3. Start the backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 4. In separate terminals, launch the front-ends
streamlit run apps/patient_intake.py   --server.port 8501
streamlit run apps/nurse_portal.py     --server.port 8502
streamlit run apps/results_portal.py   --server.port 8503
```

> **Note:** the apps use a hard-coded LAN IP (`192.168.1.191`) so phones on the same Wi-Fi can
> scan the QR codes during a live demo. Replace it with your own machine's IP in
> `backend/main.py`, `apps/patient_intake.py`, `apps/nurse_portal.py`, and `apps/results_portal.py`.

## Tech stack

FastAPI · Streamlit · Google Gemini (2.5 Flash) · Pydantic · qrserver.com QR API

## Team

Built by team **Byte** at the HSIL Hackathon, Beirut.


## Repository note

Large pitch-deck files, participant certificates, and development backups are intentionally omitted from this public repository. The application source code and runtime behavior are unchanged.

# 🧠 MindBridge AI — AI-Powered Mental Health Support Platform

<div align="center">

[![License: Llama 3](https://img.shields.io/badge/License-Meta_Llama_3-blue.svg)](https://llama.meta.com/llama3/license/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_Next.js-61DAFB.svg)](https://nextjs.org/)
[![PEFT](https://img.shields.io/badge/Fine--Tuning-QLoRA_4bit-orange.svg)](https://github.com/huggingface/peft)

**A domain-specialized, empathetic mental wellness companion fine-tuned on Meta Llama-3-8B-Instruct with QLoRA.**

*Built with Meta Llama 3*

</div>

---

## 📌 1. Project Overview

**MindBridge AI** is an end-to-end mental wellness and conversational support platform designed to assist students and individuals coping with academic pressure, exam anxiety, loneliness, burnout, and emotional distress.

### Key Capabilities:
- **Domain Fine-Tuned LLM:** Meta Llama-3-8B fine-tuned using QLoRA for empathetic, non-judgmental conversational support.
- **Multi-Layer Safety Engine:** Deterministic input/output filtering preventing unauthorized medical diagnoses, psychiatric prescriptions, and violence.
- **Crisis Escalation:** Immediate detection of self-harm / suicidal ideation with localized emergency hotline intervention.
- **Semantic Memory & Tracking:** Redis-backed short-term conversation context and PostgreSQL long-term history.
- **Mood Tracking & Journaling:** Daily emotional logging, trend analytics, and a private reflection journal.

> **Medical Disclaimer:** MindBridge AI is an AI emotional-support assistant created for psychoeducation and wellness reflection. It is **NOT** a certified diagnostic medical tool, does **NOT** provide clinical diagnoses, and does **NOT** prescribe medication. Users in crisis are directed to professional human helplines.

---

## 🏗️ 2. System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   Next.js / React Frontend             │
│   (Chat Interface, Mood Tracker, Private Journal)      │
└───────────────────────────┬────────────────────────────┘
                            │ REST / JSON (with JWT Auth)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend Service                │
│                 (Port: 8000 /api/v1)                   │
├────────────────────────────────────────────────────────┤
│ • Authentication (JWT, bcrypt password hashing)        │
│ • Database (PostgreSQL: Users, Chats, Moods, Journal)  │
│ • Cache & Memory (Redis: 24h Conversation Memory)      │
│ • Sentence-Transformers (Relevance & Semantic Search)  │
│ • Emotion Classifier (DistilBERT Mood Detector)        │
└───────────────────────────┬────────────────────────────┘
                            │ Internal HTTP (Port: 8001)
                            ▼
┌────────────────────────────────────────────────────────┐
│               MindBridge Safety Layer                  │
├────────────────────────────────────────────────────────┤
│ 1. Input Safety Filter (Crisis Regex & Keyword Guards) │
│ 2. System Prompt Injection (Domain Rules & Boundaries) │
│ 3. Output Sanitizer (Prohibits Clinical Claims)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│       Dedicated Model Inference Server (Port: 8001)    │
│       Meta Llama 3 8B Instruct + MindBridge LoRA       │
└────────────────────────────────────────────────────────┘
```

---

## 🔬 3. Model & Fine-Tuning Specifications

| Parameter | Configuration |
|-----------|---------------|
| **Base Model** | [`meta-llama/Meta-Llama-3-8B-Instruct`](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) |
| **Fine-Tuning Method** | QLoRA (4-bit NF4 Quantization + LoRA) |
| **LoRA Rank / Alpha** | $r = 16$, $\alpha = 32$, Dropout = 0.05 |
| **Target Modules** | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| **Training Dataset** | 775 Curated Mental Health Dialogues |
| **Validation Dataset**| 87 Curated Dialogues |
| **Epochs** | **1 Epoch** |
| **Sequence Length** | 256 tokens |
| **Batch Size** | 1 (per device) $\times$ 4 Gradient Accumulation Steps = Effective Batch 4 |
| **Optimizer** | Paged AdamW 8-bit ($lr = 2 \times 10^{-4}$) |

---

## 🚀 4. Step-by-Step Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Mindbridge_ai.git
cd Mindbridge_ai
```

### Step 2: Start Infrastructure (PostgreSQL & Redis)
```bash
docker-compose up -d
```
*Starts PostgreSQL on port `5435` and Redis on port `6380`.*

### Step 3: Configure Environment Variables
Copy the example environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Edit `backend/.env`:
```ini
JWT_SECRET_KEY=your_secure_random_jwt_secret_key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5435/mindbridge
REDIS_URL=redis://localhost:6380
MINDBRIDGE_BASE_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
MINDBRIDGE_ADAPTER_ID=YOUR_USERNAME/Llama-3-MindBridge
INFERENCE_URL=http://localhost:8001/generate
```

---

## 🤖 5. Model Loading & Inference Server

### Option A: Upload Fine-Tuned Adapter to Hugging Face (Recommended)
From your Google Colab training notebook or terminal:
```bash
python docs/upload_adapter_to_hf.py --repo_id "YOUR_USERNAME/Llama-3-MindBridge" --adapter_dir "/path/to/final_adapter"
```

### Option B: Local Adapter Storage
Download `mindbridge-llm-adapter.zip` from Colab and extract it into:
```text
training/models/mindbridge-llm/
├── adapter_config.json
├── adapter_model.safetensors
└── tokenizer_config.json
```

### Start the Dedicated Model Inference Server:
```bash
cd model_inference
pip install -r requirements.txt
python server.py
```
*Inference microservice starts on `http://localhost:8001`.*

---

## 💻 6. Running Backend & Frontend

### Start FastAPI Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Backend API docs available at: `http://localhost:8000/docs`*

### Start Next.js Frontend:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`.*

---

## 🧪 7. Verification & Evaluation

### 1. Verify Model Loading:
```bash
python test_model.py
```
*Loads the base model, attaches the LoRA adapter, and runs a test conversation.*

### 2. Verify Inference Service Status:
```bash
curl http://localhost:8001/model/status
```

### 3. Run Academic Evaluation Suite:
```bash
python evaluation/evaluate_model.py
```
*Evaluates the model across 15 standard clinical scenarios and outputs reports to `evaluation/results/`.*

---

## 🛡️ 8. Safety & Crisis Management

MindBridge implements a 3-stage deterministic safety architecture:
1. **Input Guard:** Real-time regex and embedding matching on self-harm, suicidal intent, and violence.
2. **Crisis Response:** Automatically returns verified Government of India emergency and mental health resources:
   - **Unified Emergency:** **112** (Immediate Police, Ambulance, Fire)
   - **Tele-MANAS (Govt of India):** **14416** or **1800-89-14416** (24×7 National Tele-Mental Health)
   - **NIMHANS Helpline:** **080-46110007** (24×7 National Apex Institute)
   - **Vandrevala Foundation:** **9999 666 555** / **1860-2662-345** (24×7 Free Psychological Support)
   - **iCall (TISS):** **9152987821** (Mon–Sat, 8 AM – 10 PM)
3. **Output Sanitizer:** Verifies that model responses never claim doctor status, diagnose clinical illnesses, or prescribe pharmaceuticals.

---

## 📄 9. License & Attribution

- **Base Model:** Meta Llama 3 ([Meta Llama 3 Community License](https://llama.meta.com/llama3/license/))
- **Source Code:** MIT License
- *Attribution: Built with Meta Llama 3.*

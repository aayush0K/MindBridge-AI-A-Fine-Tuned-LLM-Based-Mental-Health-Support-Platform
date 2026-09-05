# 🌐 MindBridge AI — Remote GPU Inference Deployment Guide

This guide explains how to host your fine-tuned **Meta Llama-3-8B-Instruct + aayush0K/Llama-3-MindBridge** model on a **Remote GPU Server** while keeping your **Next.js frontend, FastAPI backend, PostgreSQL database, and Redis cache running locally or in Docker on your PC**.

---

## 📊 1. Remote GPU Hosting Options Comparison

| Platform | Cost | GPU Specs | Setup Time | Public HTTPS URL | Best For |
|---|:---:|:---:|:---:|:---:|---|
| **Google Colab (Recommended)** | **FREE** | Tesla T4 (15 GB VRAM) | **< 3 minutes** | Yes (via free ngrok tunnel) | **Final-Year Project Demonstrations & Viva** |
| **RunPod** | ~$0.20 / hour | RTX 3090 / A4000 (16-24 GB) | ~5 minutes | Yes (built-in HTTP proxy) | Always-on 24/7 production deployment |
| **Hugging Face Spaces** | $0.60 / hour (GPU) | Nvidia T4 / A10G | ~10 minutes | Yes (built-in HTTPS) | Cloud web applications |
| **AWS / GCP GPU** | High ($1.00+/hr) | Nvidia T4 (g4dn.xlarge) | Complex | Yes | Enterprise production |

> **Recommendation for Student Project:**
> Use **Google Colab with ngrok** for project evaluations, viva demonstrations, and testing. It costs **$0.00**, takes **3 minutes to start**, and provides a dedicated **Tesla T4 (15 GB VRAM)** GPU that generates empathetic responses in real-time.

---

## 🚀 2. Option A: Google Colab Remote Server (3-Minute Setup)

### Step 1: Open Colab
1. Go to [Google Colab](https://colab.research.google.com).
2. Open or upload [`training/MindBridge_Remote_GPU_Inference.ipynb`](../training/MindBridge_Remote_GPU_Inference.ipynb).
3. In the top menu, select: **Runtime $\rightarrow$ Change runtime type $\rightarrow$ T4 GPU**.

### Step 2: Run Step 1 & 2 in Colab
- Execute **Step 1: Install Dependencies**.
- Execute **Step 2: Authenticate with Hugging Face** (enter your HF Access Token with access to Meta Llama 3).

### Step 3: Configure Ngrok & Run Step 3
1. Get your free ngrok Authtoken from [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken).
2. Paste it into the `NGROK_AUTH_TOKEN` variable in Cell 3:
   ```python
   NGROK_AUTH_TOKEN = "your_actual_ngrok_authtoken_here"
   ```
3. Run the cell. The server will:
   - Load `meta-llama/Meta-Llama-3-8B-Instruct` in 4-bit NF4 precision (~5.2 GB VRAM).
   - Attach `aayush0K/Llama-3-MindBridge` via PEFT.
   - Start the FastAPI inference service.
   - Print your public HTTPS URL:
     ```text
     =================================================================
     🎉 YOUR REMOTE GPU INFERENCE SERVER IS LIVE!
     =================================================================
     🔗 Public Base URL   : https://xxxx-xx-xx-xx.ngrok-free.app
     🔗 Inference Endpoint: https://xxxx-xx-xx-xx.ngrok-free.app/generate
     =================================================================
     ```

---

## 🧪 3. Test Remote Inference Independently

Before connecting your local website, verify that your remote GPU is generating responses from your fine-tuned model:

From your local PC PowerShell terminal, run:
```powershell
python test_remote_inference.py --url https://xxxx-xx-xx-xx.ngrok-free.app
```

> **Expected Output:**
> ```text
> 🧠 MindBridge AI — Remote GPU Model Verification
> 📡 Step 1: Checking Server Health (/health)...
> ✅ Health Check Status: 200
>    • Base Model Loaded    : True
>    • LoRA Adapter Loaded  : True
>    • Adapter Source       : aayush0K/Llama-3-MindBridge
>    • CUDA GPU Available   : True
>    • Device               : cuda
>    • Quantization         : 4-bit (NF4)
>    • VRAM Allocated (GB)  : 5.23
>
> 🧪 Step 3: Testing Model Generation (/generate)...
> ✅ Generation Successful in 2.15s!
>
> 🤖 MindBridge Model Response:
> I hear how overwhelming and heavy this exam stress feels right now. When exams pile up, our nervous system can go into overdrive. Let's take a gentle pause together...
> ```

---

## 💻 4. Connect Your Local FastAPI Backend

### Step 1: Update `backend/.env`
Open [`backend/.env`](../backend/.env) on your local PC and update `INFERENCE_URL`:
```ini
MINDBRIDGE_BASE_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
MINDBRIDGE_ADAPTER_ID=aayush0K/Llama-3-MindBridge

# Paste your live Colab/RunPod public URL here:
INFERENCE_URL=https://xxxx-xx-xx-xx.ngrok-free.app/generate

# Optional: if you configured an API key
REMOTE_INFERENCE_API_KEY=
```

---

## 🏁 5. Start Your Local Application

### Terminal 1: Start FastAPI Backend (Port 8000)
```powershell
cd d:\Final_year_project\Mindbridge_ai\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Start Next.js Frontend (Port 3000)
```powershell
cd d:\Final_year_project\Mindbridge_ai\frontend
npm run dev
```

### Terminal 3 (Browser): Open MindBridge
Open **[http://localhost:3000](http://localhost:3000)** $\rightarrow$ Log in $\rightarrow$ Open Chat $\rightarrow$ Send a message!

---

## 🛡️ 6. Graceful Offline Handling

If your remote Colab session disconnects or is stopped:
- The FastAPI backend logs the exact connection error.
- The UI receives a clean, friendly notification:
  > *"MindBridge AI model service is temporarily unavailable. Please check that your remote GPU inference server is running and try again."*
- **No confidential tokens or stack traces are leaked to the user.**
- **No external third-party models (Gemini/OpenAI) are invoked.**

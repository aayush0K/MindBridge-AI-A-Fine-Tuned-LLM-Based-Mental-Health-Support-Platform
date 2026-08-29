"""
MindBridge AI — Standalone Remote GPU Inference Server
======================================================
Designed to run on Google Colab (Tesla T4), RunPod, or any cloud GPU instance.
Loads Meta Llama 3 8B Instruct + aayush0K/Llama-3-MindBridge in 4-bit NF4 precision
and exposes a public HTTPS API.

Usage on Google Colab:
----------------------
1. In Colab, select: Runtime -> Change runtime type -> T4 GPU.
2. Run:
   !pip install -q fastapi uvicorn pydantic torch transformers peft bitsandbytes accelerate pyngrok huggingface_hub
3. Execute this script:
   python remote_gpu_server.py --ngrok_token "YOUR_NGROK_AUTHTOKEN" [--api_key "YOUR_SECRET_KEY"]
"""

import os
import sys
import time
import argparse
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

# ── Parse Arguments ───────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="MindBridge AI Remote GPU Inference Server")
parser.add_argument("--base_model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct")
parser.add_argument("--adapter_id", type=str, default="aayush0K/Llama-3-MindBridge")
parser.add_argument("--port", type=int, default=8001)
parser.add_argument("--api_key", type=str, default=os.getenv("REMOTE_INFERENCE_API_KEY", ""))
parser.add_argument("--ngrok_token", type=str, default=os.getenv("NGROK_AUTHTOKEN", ""))
args, _ = parser.parse_known_args()

# ── PyTorch & Model Imports ───────────────────────────────────────────────────
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# ── Data Schemas ──────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class InferenceRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = None
    message: Optional[str] = None
    prompt: Optional[str] = None
    temperature: float = Field(default=0.6, ge=0.0, le=2.0)
    max_new_tokens: int = Field(default=300, ge=1, le=2048)

class InferenceResponse(BaseModel):
    response: str
    model: str
    generation_time_ms: float

# ── Model Manager ─────────────────────────────────────────────────────────────
class RemoteModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.adapter_loaded = False
        self.quantization = "none"

    def load(self):
        print("\n" + "=" * 65)
        print("🧠 MindBridge AI — Loading Model on Remote GPU...")
        print("=" * 65)
        print(f"Base Model : {args.base_model}")
        print(f"LoRA Adapter: {args.adapter_id}")
        print(f"Device     : {self.device}")
        if torch.cuda.is_available():
            print(f"GPU Name   : {torch.cuda.get_device_name(0)}")
            print(f"VRAM Total : {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        print("=" * 65 + "\n")

        print(f"📦 Step 1: Loading Tokenizer from {args.base_model}...")
        self.tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"📦 Step 2: Loading Base Model in 4-bit NF4...")
        compute_dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=compute_dtype
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            quantization_config=bnb_config if self.device == "cuda" else None,
            device_map="auto" if self.device == "cuda" else "cpu",
            torch_dtype=compute_dtype if self.device == "cuda" else torch.float32,
            trust_remote_code=True
        )
        self.quantization = "4-bit (NF4)" if self.device == "cuda" else "float32 (CPU)"

        print(f"📦 Step 3: Attaching LoRA Adapter '{args.adapter_id}' from Hugging Face Hub...")
        try:
            self.model = PeftModel.from_pretrained(base_model, args.adapter_id)
            self.adapter_loaded = True
            print(f"✅ MindBridge LoRA Adapter successfully attached from Hugging Face: {args.adapter_id}")
        except Exception as e:
            print(f"⚠️ Failed to load adapter from Hugging Face ({e}). Running base model directly.")
            self.model = base_model

        self.model.eval()
        print("✅ Remote model initialized and ready in memory!\n")

    def get_status(self):
        vram_allocated = 0.0
        if torch.cuda.is_available():
            vram_allocated = round(torch.cuda.memory_allocated() / (1024**3), 2)
        return {
            "base_model": args.base_model,
            "adapter": args.adapter_id,
            "model_loaded": self.model is not None,
            "adapter_loaded": self.adapter_loaded,
            "cuda_available": torch.cuda.is_available(),
            "device": str(self.device),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
            "quantization": self.quantization,
            "vram_allocated_gb": vram_allocated
        }

model_manager = RemoteModelManager()

# ── FastAPI App Setup ─────────────────────────────────────────────────────────
app = FastAPI(
    title="MindBridge AI — Remote GPU Inference Server",
    description="Dedicated remote GPU endpoint for Meta Llama-3-8B + aayush0K/Llama-3-MindBridge",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Header(default=None)
):
    if not args.api_key or not args.api_key.strip():
        return True
    if x_api_key and x_api_key.strip() == args.api_key.strip():
        return True
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip() == args.api_key.strip():
            return True
    raise HTTPException(status_code=401, detail="Unauthorized: Invalid MindBridge API Key.")

@app.on_event("startup")
def on_startup():
    model_manager.load()

@app.get("/")
def root():
    return {
        "service": "MindBridge AI Remote GPU Inference Service",
        "status": "ready" if model_manager.model else "not_loaded",
        "base_model": args.base_model,
        "adapter": args.adapter_id,
        "attribution": "Built with Meta Llama 3"
    }

@app.get("/health")
def health():
    return model_manager.get_status()

@app.get("/model/status", dependencies=[Depends(verify_api_key)])
def model_status():
    return model_manager.get_status()

@app.post("/generate", response_model=InferenceResponse, dependencies=[Depends(verify_api_key)])
def generate(request: InferenceRequest):
    if not model_manager.model or not model_manager.tokenizer:
        raise HTTPException(status_code=503, detail="MindBridge model is not loaded.")

    start_time = time.time()

    if request.messages:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    elif request.message:
        messages_dict = [
            {"role": "system", "content": "You are MindBridge, an empathetic, supportive mental health AI companion. Provide compassionate, non-judgmental validation and practical coping strategies without medical diagnoses or prescriptions."},
            {"role": "user", "content": request.message}
        ]
    elif request.prompt:
        messages_dict = [
            {"role": "system", "content": "You are MindBridge, an empathetic, supportive mental health AI companion. Provide compassionate, non-judgmental validation and practical coping strategies without medical diagnoses or prescriptions."},
            {"role": "user", "content": request.prompt}
        ]
    else:
        raise HTTPException(status_code=422, detail="Missing required field: 'messages', 'message', or 'prompt'.")

    try:
        prompt = model_manager.tokenizer.apply_chat_template(
            messages_dict, tokenize=False, add_generation_prompt=True
        )
        inputs = model_manager.tokenizer(prompt, return_tensors="pt").to(model_manager.model.device)

        with torch.no_grad():
            outputs = model_manager.model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=model_manager.tokenizer.eos_token_id
            )

        generated_text = model_manager.tokenizer.decode(
            outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference generation error: {str(e)}")

    generation_time = (time.time() - start_time) * 1000

    return InferenceResponse(
        response=generated_text.strip(),
        model=f"Llama-3-MindBridge ({args.adapter_id})",
        generation_time_ms=generation_time
    )

def start_server():
    # If ngrok token provided, expose public HTTPS URL
    if args.ngrok_token and args.ngrok_token.strip():
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(args.ngrok_token.strip())
            public_tunnel = ngrok.connect(args.port)
            print("\n" + "=" * 65)
            print("🌐 PUBLIC HTTPS INFERENCE URL CREATED:")
            print(f"🔗 Public URL : {public_tunnel.public_url}")
            print(f"🔗 Target URL : {public_tunnel.public_url}/generate")
            print("=" * 65)
            print("\n👉 Copy this URL and set it in your local backend/.env:")
            print(f"INFERENCE_URL={public_tunnel.public_url}/generate\n")
        except Exception as e:
            print(f"⚠️ Could not start ngrok tunnel: {e}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    start_server()

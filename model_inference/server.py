from fastapi import FastAPI, HTTPException, Header, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from contextlib import asynccontextmanager
import time
import os
import torch
import uvicorn
from typing import Optional

try:
    from .schemas import InferenceRequest, InferenceResponse, ChatMessage
    from .model_loader import model_manager
    from .config import settings
except ImportError:  # pragma: no cover - supports running file directly
    from schemas import InferenceRequest, InferenceResponse, ChatMessage
    from model_loader import model_manager
    from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Header(default=None)
):
    """Enforces API Key check if settings.API_KEY is defined."""
    if not settings.API_KEY or not settings.API_KEY.strip():
        return True  # No API key required

    # 1. Check X-API-Key header
    if x_api_key and x_api_key.strip() == settings.API_KEY.strip():
        return True

    # 2. Check Bearer token in Authorization header
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            if parts[1].strip() == settings.API_KEY.strip():
                return True

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Invalid or missing MindBridge Remote Inference API Key."
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model once on startup
    print("=" * 60)
    print("🚀 Initializing MindBridge Dedicated Inference Service...")
    print(f"Base Model : {settings.BASE_MODEL}")
    print(f"Adapter ID : {settings.ADAPTER_ID}")
    print("=" * 60)
    try:
        model_manager.load_model()
    except Exception as e:
        print(f"❌ Failed to load model on startup: {str(e)}")
    yield
    # Cleanup on shutdown
    model_manager.model = None
    model_manager.tokenizer = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("🛑 MindBridge Inference Service shutdown complete.")

app = FastAPI(
    title="MindBridge AI — Dedicated Remote GPU Inference Service",
    description="Fine-tuned Meta Llama-3-8B + QLoRA model server for MindBridge AI",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    status = model_manager.get_status()
    return {
        "service": "MindBridge AI Remote GPU Inference Service",
        "base_model": settings.BASE_MODEL,
        "adapter": settings.ADAPTER_ID,
        "status": "ready" if model_manager.model else "not_loaded",
        "cuda_available": status.get("gpu_available", False),
        "device": status.get("device", "unknown"),
        "attribution": "Built with Meta Llama 3"
    }

@app.get("/health")
async def health():
    return model_manager.get_status()

@app.get("/model/status", dependencies=[Depends(verify_api_key)])
async def model_status():
    """Detailed model verification endpoint."""
    return model_manager.get_status()

@app.post("/generate", response_model=InferenceResponse, dependencies=[Depends(verify_api_key)])
async def generate(request: InferenceRequest):
    if not model_manager.model or not model_manager.tokenizer:
        raise HTTPException(
            status_code=503,
            detail="MindBridge model is not loaded on this server. Please ensure GPU memory and model weights are ready."
        )

    start_time = time.time()

    # Normalize messages format
    if request.messages:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    elif request.message:
        messages_dict = [
            {"role": "system", "content": "You are MindBridge, an empathetic, supportive mental health AI companion. Provide warm, non-judgmental validation and practical coping strategies without medical diagnoses or prescriptions."},
            {"role": "user", "content": request.message}
        ]
    elif request.prompt:
        messages_dict = [
            {"role": "system", "content": "You are MindBridge, an empathetic, supportive mental health AI companion. Provide warm, non-judgmental validation and practical coping strategies without medical diagnoses or prescriptions."},
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
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    generation_time = (time.time() - start_time) * 1000  # ms

    return InferenceResponse(
        response=generated_text.strip(),
        model=f"Llama-3-MindBridge ({model_manager.adapter_source})",
        generation_time_ms=generation_time
    )

if __name__ == "__main__":
    uvicorn.run("model_inference.server:app", host=settings.HOST, port=settings.PORT, reload=False)

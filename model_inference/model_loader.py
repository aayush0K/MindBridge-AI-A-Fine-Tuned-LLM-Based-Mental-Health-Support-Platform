import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from .config import settings

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = settings.DEVICE
        self.adapter_loaded = False
        self.adapter_source = None
        self.quantization = "none"

    def load_model(self):
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_available}")
        
        if not cuda_available:
            print("⚠️ WARNING: No CUDA GPU detected. MindBridge Llama-3-8B requires a suitable GPU for practical real-time inference.")
            self.device = "cpu"
        else:
            self.device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"Detected GPU: {gpu_name} ({vram_gb:.2f} GB VRAM)")

        print(f"Loading Tokenizer: {settings.BASE_MODEL}...")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.BASE_MODEL, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.device == "cuda":
            print("Loading Base Model in 4-bit NF4 (CUDA)...")
            compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=compute_dtype
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=compute_dtype,
                trust_remote_code=True
            )
            self.quantization = "4-bit (NF4)"
        else:
            print("Loading Base Model on CPU (Slow fallback)...")
            base_model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL,
                device_map="cpu",
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            self.quantization = "none (float32)"

        # ── Check Adapter Sources ─────────────────────────────────────────────
        # 1. Check if Hugging Face Adapter ID is configured
        if settings.ADAPTER_ID and settings.ADAPTER_ID.strip():
            hf_id = settings.ADAPTER_ID.strip()
            print(f"Attempting to load MindBridge LoRA Adapter from Hugging Face Hub: {hf_id}...")
            try:
                self.model = PeftModel.from_pretrained(base_model, hf_id)
                self.adapter_loaded = True
                self.adapter_source = f"HuggingFace: {hf_id}"
                print(f"✅ MindBridge LoRA Adapter successfully attached from Hugging Face: {hf_id}")
            except Exception as e:
                print(f"⚠️ Failed to load adapter from Hugging Face ({e}). Checking local paths...")

        # 2. Check local path if not loaded from HF
        if not self.adapter_loaded:
            candidate_paths = [
                settings.ADAPTER_PATH,
                "../training/models/mindbridge-llm",
                "./training/models/mindbridge-llm",
                "../model/mindbridge-llama3",
                "./model/mindbridge-llama3",
                "../epoch1/final_adapter",
                "./epoch1/final_adapter"
            ]
            for path in candidate_paths:
                if os.path.exists(path) and (
                    os.path.exists(os.path.join(path, "adapter_config.json")) or
                    os.path.exists(os.path.join(path, "adapter_model.safetensors"))
                ):
                    try:
                        print(f"Loading MindBridge LoRA Adapter from local path: {path}...")
                        self.model = PeftModel.from_pretrained(base_model, path)
                        self.adapter_loaded = True
                        self.adapter_source = f"Local: {path}"
                        print(f"✅ MindBridge LoRA Adapter successfully attached from: {path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Error loading adapter from {path}: {e}")

        if not self.adapter_loaded:
            print("⚠️ No fine-tuned adapter found. Running with base Llama-3 model directly.")
            self.model = base_model
            self.adapter_source = "None (Base Model Only)"

        self.model.eval()
        print("✅ ModelManager initialization complete.")

    def get_status(self) -> dict:
        """Returns the status and health of the model manager."""
        vram_allocated = 0.0
        if torch.cuda.is_available():
            vram_allocated = round(torch.cuda.memory_allocated() / (1024**3), 2)

        return {
            "base_model": settings.BASE_MODEL,
            "base_model_loaded": self.model is not None,
            "adapter_loaded": self.adapter_loaded,
            "adapter_source": self.adapter_source,
            "tokenizer_loaded": self.tokenizer is not None,
            "gpu_available": torch.cuda.is_available(),
            "device": str(self.device),
            "quantization": self.quantization,
            "vram_allocated_gb": vram_allocated
        }

model_manager = ModelManager()

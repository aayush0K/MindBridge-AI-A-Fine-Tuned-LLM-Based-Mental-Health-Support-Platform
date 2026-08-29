"""
MindBridge AI — Standalone Model Verification Script
===================================================
Phase 1: Verifies that the Base Meta Llama-3-8B model and the
MindBridge QLoRA fine-tuned adapter can be loaded and run for inference.

Usage:
    python test_model.py [--adapter_path ./training/models/mindbridge-llm]
"""

import sys
import os
import argparse
import time
import torch

def parse_args():
    parser = argparse.ArgumentParser(description="Test MindBridge Fine-Tuned Llama-3 Model")
    parser.add_argument(
        "--base_model",
        type=str,
        default="meta-llama/Meta-Llama-3-8B-Instruct",
        help="Base model HuggingFace repository ID"
    )
    parser.add_argument(
        "--adapter_path",
        type=str,
        default="./training/models/mindbridge-llm",
        help="Path to the fine-tuned LoRA adapter folder"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="I'm feeling very stressed about my upcoming exams and I can't concentrate.",
        help="Test prompt to evaluate"
    )
    return parser.parse_args()

def check_hardware():
    print("=" * 60)
    print("🧠 MindBridge AI — Hardware & Environment Check")
    print("=" * 60)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU Name: {gpu_name}")
        print(f"Total VRAM: {vram_gb:.2f} GB")
        if vram_gb < 6.0:
            print("⚠️ WARNING: GPU VRAM is under 6GB. Loading 8B models may require strict 4-bit quantization.")
    else:
        print("⚠️ NOTE: Running without CUDA GPU. Local 8B parameter loading is not recommended on CPU.")
    print("=" * 60 + "\n")
    return cuda_available

def load_and_test(base_model_name: str, adapter_path: str, user_prompt: str):
    cuda_available = check_hardware()
    
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    
    print(f"📦 Step 1: Loading Tokenizer for {base_model_name}...")
    start_t = time.time()
    try:
        tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        print(f"✅ Tokenizer loaded in {time.time() - start_t:.2f}s")
    except Exception as e:
        print(f"❌ Failed to load tokenizer: {e}")
        return False

    print(f"\n📦 Step 2: Loading Base Model ({base_model_name})...")
    start_t = time.time()
    try:
        if cuda_available:
            compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=compute_dtype
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=compute_dtype,
                trust_remote_code=True
            )
        else:
            print("Loading in float32 on CPU (will take several minutes)...")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                device_map="cpu",
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
        print(f"✅ Base Model loaded in {time.time() - start_t:.2f}s")
    except Exception as e:
        print(f"❌ Failed to load base model: {e}")
        print("Tip: If you see a gated repo error, ensure you have run `huggingface-cli login`.")
        return False

    print(f"\n📦 Step 3: Checking & Loading LoRA Adapter from '{adapter_path}'...")
    start_t = time.time()
    adapter_found = False

    # 1. First check if adapter_path is a HuggingFace Hub Repo ID (e.g., 'username/Llama-3-MindBridge')
    if "/" in adapter_path and not os.path.exists(adapter_path):
        print(f"Attempting to load from Hugging Face Hub: '{adapter_path}'...")
        try:
            model = PeftModel.from_pretrained(base_model, adapter_path)
            print(f"✅ MindBridge LoRA Adapter successfully downloaded & attached from Hugging Face Hub: {adapter_path} in {time.time() - start_t:.2f}s")
            adapter_found = True
        except Exception as e:
            print(f"⚠️ Could not load directly from Hugging Face Hub ({e}). Checking local folders...")

    # 2. Check local directories if not loaded from HF Hub
    if not adapter_found:
        candidate_paths = [
            adapter_path,
            "./model/mindbridge-llama3",
            "./epoch1/final_adapter",
            "./training/models/mindbridge-llm"
        ]
        
        selected_adapter = None
        for path in candidate_paths:
            if os.path.exists(path) and (
                os.path.exists(os.path.join(path, "adapter_config.json")) or
                os.path.exists(os.path.join(path, "adapter_model.safetensors"))
            ):
                selected_adapter = path
                break

        if selected_adapter:
            try:
                model = PeftModel.from_pretrained(base_model, selected_adapter)
                print(f"✅ MindBridge LoRA Adapter successfully attached from local path: {selected_adapter} in {time.time() - start_t:.2f}s")
                adapter_found = True
            except Exception as e:
                print(f"⚠️ Could not load adapter from {selected_adapter}: {e}")
                print("Falling back to raw base model for testing...")
                model = base_model
        else:
            print(f"⚠️ No LoRA adapter files found locally in ({candidate_paths}) or on Hugging Face.")
            print("Testing inference using Base Llama-3 model directly.")
            model = base_model

    model.eval()

    # Step 4: Generate response
    print("\n" + "=" * 60)
    print("🧪 Step 4: Running Inference Test")
    print("=" * 60)
    print(f"User Prompt: \"{user_prompt}\"\n")

    system_prompt = (
        "You are MindBridge, an empathetic, supportive AI mental wellness companion. "
        "Your role is to provide compassionate, non-judgmental support, emotional validation, "
        "and practical coping suggestions. You do not provide medical diagnoses or prescribe medication."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    print("Generating response...")
    gen_start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.6,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    gen_time = time.time() - gen_start

    output_tokens = outputs[0][len(inputs.input_ids[0]):]
    generated_text = tokenizer.decode(output_tokens, skip_special_tokens=True).strip()

    print("\n" + "-" * 60)
    print(f"🤖 MindBridge Response (Generated in {gen_time:.2f}s):")
    print("-" * 60)
    print(generated_text)
    print("-" * 60)
    print("\n✅ Verification Successful! The model pipeline is functional.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    args = parse_args()
    success = load_and_test(args.base_model, args.adapter_path, args.prompt)
    sys.exit(0 if success else 1)

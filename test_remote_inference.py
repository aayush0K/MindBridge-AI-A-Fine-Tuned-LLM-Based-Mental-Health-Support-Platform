"""
MindBridge AI — Remote GPU Model Verification Script
====================================================
Tests a remote (or local) GPU inference endpoint running Meta Llama 3 8B + aayush0K/Llama-3-MindBridge.

Usage:
    python test_remote_inference.py --url https://your-gpu-server-url.ngrok-free.app [--api_key YOUR_KEY]
"""

import argparse
import sys
import time
import httpx

def main():
    parser = argparse.ArgumentParser(description="Verify MindBridge Remote GPU Inference Server")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8001",
        help="Base URL of the remote GPU server (e.g. https://xxxx.ngrok-free.app or http://localhost:8001)"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default="",
        help="Optional API key for authentication"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="I'm feeling very stressed about my upcoming exams and I can't concentrate.",
        help="Prompt to test"
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    headers = {}
    if args.api_key:
        headers["X-API-Key"] = args.api_key
        headers["Authorization"] = f"Bearer {args.api_key}"

    print("=================================================================")
    print("[MindBridge AI] Remote GPU Model Verification")
    print("=================================================================")
    print(f"Target Server : {base_url}")
    print(f"Auth Enabled  : {bool(args.api_key)}")
    print(f"Test Prompt   : \"{args.prompt}\"")
    print("=================================================================\n")

    client = httpx.Client(timeout=60.0, headers=headers)

    # ── 1. Test /health ───────────────────────────────────────────────────────
    print(">> Step 1: Checking Server Health (/health)...")
    try:
        res = client.get(f"{base_url}/health")
        res.raise_for_status()
        health_data = res.json()
        print(f"[SUCCESS] Health Check Status: {res.status_code}")
        print(f"   * Base Model Loaded    : {health_data.get('base_model_loaded')}")
        print(f"   * LoRA Adapter Loaded  : {health_data.get('adapter_loaded')}")
        print(f"   * Adapter Source       : {health_data.get('adapter')}")
        print(f"   * CUDA GPU Available   : {health_data.get('cuda_available')}")
        print(f"   * Device               : {health_data.get('device')}")
        print(f"   * Quantization         : {health_data.get('quantization')}")
        print(f"   * VRAM Allocated (GB)  : {health_data.get('vram_allocated_gb')}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to {base_url}/health: {e}")
        print("\nTroubleshooting Tips:")
        print("1. Ensure your remote GPU server (Google Colab / RunPod) is running.")
        print("2. Verify that the public URL (ngrok / tunnel) is active and accessible.")
        print("3. Check if your API key matches the server's REMOTE_INFERENCE_API_KEY.")
        sys.exit(1)

    # ── 2. Test /model/status ─────────────────────────────────────────────────
    print("\n>> Step 2: Verifying Model Status (/model/status)...")
    try:
        res = client.get(f"{base_url}/model/status")
        res.raise_for_status()
        status_data = res.json()
        print(f"[SUCCESS] Model Status Verified:")
        print(f"   * Base Model: {status_data.get('base_model')}")
        print(f"   * Adapter   : {status_data.get('adapter')}")
    except Exception as e:
        print(f"[WARN] /model/status check returned: {e}")

    # ── 3. Test /generate ─────────────────────────────────────────────────────
    print("\n>> Step 3: Testing Model Generation (/generate)...")
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are MindBridge, an empathetic, supportive AI mental health companion. "
                    "Provide compassionate, non-judgmental support, emotional validation, "
                    "and practical coping suggestions. You do not provide medical diagnoses or prescribe medication."
                )
            },
            {
                "role": "user",
                "content": args.prompt
            }
        ],
        "temperature": 0.6,
        "max_new_tokens": 256
    }

    start_time = time.time()
    try:
        res = client.post(f"{base_url}/generate", json=payload)
        res.raise_for_status()
        gen_data = res.json()
        elapsed_sec = time.time() - start_time
        response_text = gen_data.get("response", "")
        model_name = gen_data.get("model", "")
        gen_time_ms = gen_data.get("generation_time_ms", 0.0)

        print(f"[SUCCESS] Generation Successful in {elapsed_sec:.2f}s (Server GPU time: {gen_time_ms:.1f}ms)!\n")
        print("=================================================================")
        print("MindBridge Model Response:")
        print("=================================================================")
        print(response_text)
        print("=================================================================")
        print(f"Model ID: {model_name}")

    except Exception as e:
        print(f"[ERROR] Failed to generate response: {e}")
        sys.exit(1)

    print("\n[ALL VERIFICATION CHECKS PASSED]")
    print(f"Your remote model server is ready to be connected to local FastAPI at:")
    print(f"INFERENCE_URL={base_url}/generate")

if __name__ == "__main__":
    main()

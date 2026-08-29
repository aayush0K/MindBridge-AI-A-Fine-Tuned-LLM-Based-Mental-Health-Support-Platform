"""
MindBridge AI — Upload Fine-Tuned LoRA Adapter to Hugging Face Hub
==================================================================
This script uploads the trained LoRA adapter from Google Colab or your local machine
to your Hugging Face model repository.

Usage in Google Colab:
----------------------
1. In a Colab cell, execute:
   !pip install -q huggingface_hub

2. Run this script:
   python upload_adapter_to_hf.py --repo_id "YOUR_USERNAME/Llama-3-MindBridge" --adapter_dir "/content/drive/MyDrive/MindBridge/epoch1/final_adapter"

3. Enter your Hugging Face write token when prompted.
"""

import os
import argparse
from huggingface_hub import HfApi, login

def main():
    parser = argparse.ArgumentParser(description="Upload MindBridge LoRA Adapter to Hugging Face Hub")
    parser.add_argument(
        "--repo_id",
        type=str,
        required=True,
        help="Hugging Face repo ID in format 'username/repo_name' (e.g., 'yourname/Llama-3-MindBridge')"
    )
    parser.add_argument(
        "--adapter_dir",
        type=str,
        default="/content/drive/MyDrive/MindBridge/epoch1/final_adapter",
        help="Local directory containing the adapter files"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the repository private"
    )
    args = parser.parse_args()

    adapter_path = os.path.abspath(args.adapter_dir)
    print("=" * 65)
    print("🧠 MindBridge AI — Hugging Face Adapter Uploader")
    print("=" * 65)
    print(f"Target Repository : {args.repo_id}")
    print(f"Source Directory  : {adapter_path}")
    print(f"Private Repo      : {args.private}")
    print("=" * 65 + "\n")

    if not os.path.exists(adapter_path):
        raise FileNotFoundError(
            f"❌ Adapter directory not found at: {adapter_path}\n"
            "Please check the path. If running in Colab, ensure Google Drive is mounted at /content/drive."
        )

    # Verify key files
    files = os.listdir(adapter_path)
    print(f"Found {len(files)} files in adapter directory:")
    for f in files:
        print(f"  • {f}")

    has_config = "adapter_config.json" in files
    has_weights = any(f.startswith("adapter_model") for f in files)

    if not has_config or not has_weights:
        print("\n⚠️ WARNING: The directory may be missing standard LoRA adapter files (adapter_config.json or adapter_model.safetensors).")

    print("\n🔑 Authenticating with Hugging Face Hub...")
    login()

    api = HfApi()

    print(f"\n📦 Creating repository '{args.repo_id}' (if not exists)...")
    api.create_repo(
        repo_id=args.repo_id,
        repo_type="model",
        private=args.private,
        exist_ok=True
    )

    print(f"🚀 Uploading all files from {adapter_path} to {args.repo_id}...")
    api.upload_folder(
        folder_path=adapter_path,
        repo_id=args.repo_id,
        repo_type="model",
        commit_message="Upload MindBridge Llama-3 QLoRA fine-tuned adapter"
    )

    print("\n" + "=" * 65)
    print("✅ SUCCESS! Your MindBridge adapter is live on Hugging Face:")
    print(f"🔗 https://huggingface.co/{args.repo_id}")
    print("=" * 65)
    print("\nNext Step:")
    print(f"Add the following to your backend `.env` file:")
    print(f"MINDBRIDGE_ADAPTER_ID={args.repo_id}")

if __name__ == "__main__":
    main()

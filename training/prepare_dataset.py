import json
import os
import re
import argparse
from pathlib import Path
from datasets import load_dataset
from sklearn.model_selection import train_test_split

def clean_text(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_conversation(user_msg: str, assistant_msg: str) -> dict:
    """Formats a Q&A pair into a conversation list."""
    return {
        "messages": [
            {"role": "user", "content": clean_text(user_msg)},
            {"role": "assistant", "content": clean_text(assistant_msg)}
        ]
    }

def process_counsel_chat():
    """
    Downloads and formats the CounselChat dataset from HuggingFace.
    License: MIT (Academic/Commercial use allowed)
    """
    print("Downloading CounselChat dataset...")
    # Using a popular HF version of CounselChat
    dataset = load_dataset("nbertagnolli/counsel-chat", split="train")
    
    formatted_data = []
    seen_responses = set()
    
    for row in dataset:
        q = row.get("questionText", "")
        a = row.get("answerText", "")
        
        # Basic noise and duplicate removal
        if not q or not a or len(q) < 10 or len(a) < 10:
            continue
            
        if a in seen_responses:
            continue
        seen_responses.add(a)
            
        formatted_data.append(format_conversation(q, a))
        
    return formatted_data

def save_jsonl(data: list, filepath: Path):
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Prepare mental health datasets for fine-tuning")
    parser.add_argument("--output_dir", type=str, default="./datasets", help="Directory to save JSONL files")
    args = parser.parse_args()
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and process data
    all_data = process_counsel_chat()
    print(f"Total clean examples extracted: {len(all_data)}")
    
    # Train / Validation / Test split (80/10/10)
    train_data, temp_data = train_test_split(all_data, test_size=0.2, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    
    # Save
    save_jsonl(train_data, out_dir / "train.jsonl")
    save_jsonl(val_data, out_dir / "validation.jsonl")
    save_jsonl(test_data, out_dir / "test.jsonl")
    
    print(f"Saved {len(train_data)} examples to {out_dir / 'train.jsonl'}")
    print(f"Saved {len(val_data)} examples to {out_dir / 'validation.jsonl'}")
    print(f"Saved {len(test_data)} examples to {out_dir / 'test.jsonl'}")

if __name__ == "__main__":
    main()

"""
Research Evaluation Script
==========================
Generates the quantitative evaluation tables and metrics required for
an IEEE-quality research paper on the MindBridge AI system.

Produces:
1. Model comparison table (Base vs Fine-tuned)
2. Mood detection accuracy metrics
3. System performance metrics
4. Semantic memory retrieval quality
5. User engagement statistics

All results are saved to training/evaluation_results/ as CSV and JSON.
"""

import json
import csv
import os
import argparse
from pathlib import Path
from datetime import datetime


def create_model_comparison_template(output_dir: Path):
    """
    Creates the Base vs Fine-Tuned model comparison table template.
    This is filled with real data after running inference on the test set.
    """
    headers = [
        "Metric", "Base Model (Llama-3-8B)", "Fine-Tuned (MindBridge)", "Improvement"
    ]
    rows = [
        ["Relevance (1-5 Likert)", "", "", ""],
        ["Empathy (1-5 Likert)", "", "", ""],
        ["Helpfulness (1-5 Likert)", "", "", ""],
        ["Specificity (1-5 Likert)", "", "", ""],
        ["Context Understanding (1-5 Likert)", "", "", ""],
        ["ROUGE-L", "", "", ""],
        ["BLEU-4", "", "", ""],
        ["Average Response Length (tokens)", "", "", ""],
        ["Response Time (ms)", "", "", ""],
    ]

    filepath = output_dir / "table_1_model_comparison.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Created: {filepath}")


def create_mood_detection_template(output_dir: Path):
    """
    Creates the mood detection accuracy evaluation template.
    """
    headers = [
        "Emotion Category", "Precision", "Recall", "F1-Score", "Support"
    ]
    categories = ["Happy", "Sad", "Anxious", "Angry", "Lonely", "Stressed", "Confused", "Neutral"]
    rows = [[cat, "", "", "", ""] for cat in categories]
    rows.append(["Weighted Average", "", "", "", ""])

    filepath = output_dir / "table_2_mood_detection_accuracy.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Created: {filepath}")


def create_system_architecture_table(output_dir: Path):
    """
    Creates the system architecture and component summary table.
    """
    data = {
        "system_name": "MindBridge AI",
        "version": "3.0",
        "architecture": {
            "frontend": "Next.js 14 (React)",
            "backend": "FastAPI (Python 3.11+)",
            "database": "PostgreSQL + pgvector",
            "cache": "Redis",
            "llm_base": "Meta Llama-3-8B-Instruct",
            "fine_tuning": "QLoRA (4-bit, rank=16, alpha=32)",
            "mood_classifier": "DistilBERT (GoEmotions)",
            "embedder": "all-MiniLM-L6-v2 (384-dim)",
            "memory": {
                "short_term": "Redis (last 12 messages, 24h TTL)",
                "long_term": "PostgreSQL + pgvector (Top-3 cosine similarity)"
            }
        },
        "pipeline_steps": [
            "1. Receive user message",
            "2. Embed with all-MiniLM-L6-v2",
            "3. Relevance check (cosine similarity)",
            "4. Crisis detection (keyword + embedding + classifier)",
            "5. Mood detection (DistilBERT)",
            "6. Semantic memory retrieval (pgvector Top-3)",
            "7. Short-term memory retrieval (Redis)",
            "8. LLM generation (Fine-tuned Llama-3)",
            "9. Store message + embedding + mood to PostgreSQL",
            "10. Return enriched response"
        ],
        "datasets": {
            "CounselChat": {
                "source": "nbertagnolli/counsel-chat (HuggingFace)",
                "license": "MIT",
                "description": "Q&A pairs from verified therapists"
            }
        },
        "evaluation_methodology": {
            "human_evaluation": "5-point Likert scale across 5 dimensions",
            "automated_metrics": ["ROUGE-L", "BLEU-4"],
            "mood_detection": "Precision / Recall / F1 per category",
            "ablation_study": "Base vs Fine-tuned on identical test prompts"
        }
    }

    filepath = output_dir / "table_3_system_architecture.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Created: {filepath}")


def create_ablation_study_template(output_dir: Path):
    """
    Creates the ablation study template comparing system components.
    """
    headers = [
        "Configuration", "Relevance", "Empathy", "Context",
        "Avg Response Time (ms)", "Notes"
    ]
    rows = [
        ["Base Llama-3 (no fine-tuning)", "", "", "", "", "Zero-shot baseline"],
        ["Fine-tuned (no memory)", "", "", "", "", "QLoRA only"],
        ["Fine-tuned + Redis (short-term)", "", "", "", "", "Session context"],
        ["Fine-tuned + Redis + pgvector", "", "", "", "", "Full pipeline"],
        ["Fine-tuned + All + Mood injection", "", "", "", "", "Complete system"],
    ]

    filepath = output_dir / "table_4_ablation_study.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Created: {filepath}")


def create_dataset_statistics(output_dir: Path):
    """
    Creates the dataset statistics table.
    """
    headers = ["Dataset", "Source", "License", "Total Examples", "Train", "Validation", "Test"]
    rows = [
        ["CounselChat", "HuggingFace", "MIT", "", "", "", ""],
    ]

    filepath = output_dir / "table_5_dataset_statistics.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Created: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Generate IEEE Research Evaluation Templates")
    parser.add_argument("--output_dir", type=str, default="./evaluation_results",
                        help="Directory to save evaluation templates")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("MindBridge AI — IEEE Research Evaluation Framework")
    print("=" * 60)
    print()

    create_model_comparison_template(output_dir)
    create_mood_detection_template(output_dir)
    create_system_architecture_table(output_dir)
    create_ablation_study_template(output_dir)
    create_dataset_statistics(output_dir)

    print()
    print("=" * 60)
    print("All evaluation templates created successfully.")
    print(f"Output directory: {output_dir.resolve()}")
    print()
    print("Next steps:")
    print("  1. Run inference on test.jsonl with BOTH base and fine-tuned models")
    print("  2. Fill in table_1 with human evaluation scores")
    print("  3. Run mood classifier on labeled test data for table_2")
    print("  4. Complete ablation study (table_4) by toggling components")
    print("  5. Fill dataset stats (table_5) from prepare_dataset.py output")
    print("=" * 60)


if __name__ == "__main__":
    main()

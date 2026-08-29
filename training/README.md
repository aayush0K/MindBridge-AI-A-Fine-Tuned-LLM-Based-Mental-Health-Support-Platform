# MindBridge AI: QLoRA Fine-Tuning Pipeline

This directory contains the reproducible pipeline for Phase 2 and Phase 3 of the MindBridge AI research project.
It fine-tunes an open-weight base model into a domain-specific mental health conversational model.

## 1. Setup Environment
This pipeline is designed for a CUDA-enabled GPU (e.g., Google Colab T4 or local NVIDIA RTX series).
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Dataset Preparation (Phase 2)
We use the **CounselChat** dataset (MIT License, academic use verified). It provides high-quality QA pairs from real verified therapists, teaching the model deep empathy and professional relevance.
```bash
python prepare_dataset.py
```
This script downloads, cleans HTML/noise, removes duplicates, formats the data into JSONL Llama-3 conversational style, and splits it into `train.jsonl`, `validation.jsonl`, and `test.jsonl`.

## 3. QLoRA Training (Phase 3)
We are using **Llama-3-8B-Instruct** as the base model.
*Why this model?* It has state-of-the-art instruction following for its size class, and fine-tuning an "Instruct" model yields much better multi-turn conversational flow than a raw base model.

```bash
python train_qlora.py --config configs/qlora_config.json
```
**Configuration (`configs/qlora_config.json`):**
*   `lora_r=16`, `lora_alpha=32`: Standard parameters for robust instruction tuning.
*   `learning_rate=2e-4`: Optimal for QLoRA.
*   `4-bit Quantization`: Enabled via `bitsandbytes` to fit the 8B model into ~6GB of VRAM, making it fully trainable on a free Google Colab T4.

## 4. Evaluation & Testing
To interact with your newly trained model:
```bash
python inference.py --adapter ./models/mindbridge-llm
```

To generate the Human Evaluation framework (Phase 4 Prep):
```bash
python evaluate.py
```
This generates a CSV grading template based on a 1-5 Likert scale for Relevance, Empathy, Helpfulness, Specificity, and Context Understanding.

## Limitations & Risks
*   **Hugging Face Access:** Llama-3 requires you to accept the license on HuggingFace and run `huggingface-cli login` before running `train_qlora.py`.
*   **Hardware:** While QLoRA fits on a T4, training speed depends heavily on batch size. A T4 might take 8-12 hours for 3 epochs over 2000 examples.
*   **Medical Disclaimer:** This model is fine-tuned for emotional support, NOT clinical diagnosis. Safety classifiers must remain active in production.

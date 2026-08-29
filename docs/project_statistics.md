# 📊 MindBridge AI — Project Statistics & Architecture Report

## Model & Training Configuration

```text
============================================================
MINDBRIDGE AI FINE-TUNED MODEL SPECIFICATIONS
============================================================

Base Model:                  Meta Llama 3 8B Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
Fine-Tuning Method:          QLoRA (Quantized Low-Rank Adaptation)
Quantization:                4-bit NormalFloat (NF4) with Double Quantization
Compute Precision:           BFloat16 (with float32 gradient scaler stabilization)

Training Dataset:            CounselChat Mental Health Corpus (High-Quality Curated Subset)
Training Examples:           775 Q&A Conversations
Validation Examples:         87 Q&A Conversations
Total Dataset Size:          862 Samples

Epochs:                      1
Per-Device Batch Size:       1
Gradient Accumulation Steps: 4
Effective Batch Size:        4
Max Sequence Length:         256 tokens
Learning Rate:               2e-4
Optimizer:                   Paged AdamW 8-bit
Warmup Steps:                10
Weight Decay:                0.01

LoRA Rank (r):               16
LoRA Alpha (alpha):          32
LoRA Dropout:                0.05
Target Modules:              q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
Trainable Parameters:        ~41.9 Million (0.52% of 8B base parameters)
Adapter Storage Footprint:   ~160 MB (LoRA weights + config)

Training Hardware:           NVIDIA Tesla T4 GPU (Google Colab, 15 GB VRAM)
============================================================
```

## System Architecture Pipeline

```text
┌────────────────────────────────────────────────────────┐
│                   React + Vite Frontend                │
│ (Chat UI, Mood Tracker, Private Journal, Resources)    │
└───────────────────────────┬────────────────────────────┘
                            │ (REST / JSON + JWT)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend Service                │
│                 (Port: 8000 /api/v1)                   │
├────────────────────────────────────────────────────────┤
│ • JWT Authentication & User Session Management         │
│ • PostgreSQL Database (Users, Chats, Moods, Journal)   │
│ • Redis Cache (Conversation Memory & History TTL)      │
│ • Sentence-Transformers (Relevance & Semantic Search)  │
│ • DistilBERT Emotion & Mood Classifier                 │
└───────────────────────────┬────────────────────────────┘
                            │ (Internal HTTP)
                            ▼
┌────────────────────────────────────────────────────────┐
│               MindBridge Safety Layer                  │
├────────────────────────────────────────────────────────┤
│ 1. Input Safety Guard (Crisis Regex & Risk Scoring)    │
│ 2. System Prompt Injection (Domain Rules & Empathy)    │
│ 3. Output Sanitizer (No Medical Claims / Prescriptions)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        Dedicated Inference Server (Port 8001)          │
│       Meta Llama 3 8B Instruct + MindBridge LoRA       │
└────────────────────────────────────────────────────────┘
```

## Academic Attribution

*This project is built with Meta Llama 3 under the Meta Llama 3 Community License Agreement.*

---
license: llama3
language:
- en
base_model: meta-llama/Meta-Llama-3-8B-Instruct
tags:
- mental-health
- emotional-support
- llama-3
- qlora
- peft
- conversational
pipeline_tag: text-generation
---

# 🧠 MindBridge AI — Llama-3-8B Mental Health Support Adapter

**MindBridge AI** is a domain-specialized conversational AI model fine-tuned for empathetic, supportive mental health and emotional wellness dialogue. It is designed to assist students and individuals facing academic stress, anxiety, burnout, loneliness, and emotional overwhelm.

> **Disclaimer:** MindBridge is an AI mental-wellness companion created for emotional support and psychoeducation. It is **NOT** a certified medical device, does **NOT** provide clinical diagnoses, and does **NOT** prescribe or recommend medications. It is not a replacement for licensed psychotherapy or psychiatric medical intervention.

---

## Model Details

- **Model Name:** Llama-3-MindBridge
- **Base Model:** [`meta-llama/Meta-Llama-3-8B-Instruct`](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
- **Fine-Tuning Technique:** QLoRA (4-bit NF4 Quantization + Low-Rank Adaptation)
- **Target Modules:** `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
- **LoRA Hyperparameters:**
  - Rank ($r$): 16
  - Alpha ($\alpha$): 32
  - Dropout: 0.05
  - Bias: None
- **Quantization:** 4-bit NormalFloat (NF4) with Double Quantization
- **Max Sequence Length:** 256 tokens
- **Batch Size:** 1 (per device) with 4 Gradient Accumulation Steps (Effective batch size = 4)
- **Learning Rate:** $2 \times 10^{-4}$ with Paged AdamW 8-bit optimizer
- **Epochs:** 1
- **Dataset:** 775 Curated Mental Health Training Q&As + 87 Validation Examples

---

## Intended Use & Safety

### Appropriate Use Cases:
- Providing empathetic, active listening and emotional validation.
- Suggesting evidence-informed coping techniques (box breathing, journaling, grounding exercises).
- Academic stress navigation and motivational reframing for students.
- Encouraging users to connect with qualified professionals and trusted support networks.

### Prohibited & Out-of-Scope Use Cases:
- Providing psychiatric diagnoses.
- Prescribing or recommending medication alterations.
- Replacing clinical psychotherapy or emergency crisis response.

---

## How to Load with PEFT & Transformers

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

BASE_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
ADAPTER_ID = "YOUR_USERNAME/Llama-3-MindBridge"

# 1. 4-bit Quantization Config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

# 2. Load Base Model & Tokenizer
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto"
)

# 3. Attach Fine-Tuned LoRA Adapter
model = PeftModel.from_pretrained(base_model, ADAPTER_ID)
model.eval()

# 4. Generate Response
messages = [
    {
        "role": "system",
        "content": (
            "You are MindBridge, a compassionate, empathetic AI mental health companion. "
            "Provide supportive, non-judgmental guidance. Do not diagnose or prescribe medication."
        )
    },
    {
        "role": "user",
        "content": "I am feeling overwhelmed with exam pressure and having trouble sleeping."
    }
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.6,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
print(response)
```

---

## License & Attribution

This model is built upon **Meta Llama 3** and is governed by the [Meta Llama 3 Community License](https://llama.meta.com/llama3/license/).

*Built with Meta Llama 3.*

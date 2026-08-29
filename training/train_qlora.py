import json
import torch
import argparse
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def format_prompt(sample, tokenizer):
    """
    Applies the model's chat template to the messages list.
    """
    prompt = tokenizer.apply_chat_template(sample["messages"], tokenize=False, add_generation_prompt=False)
    return {"text": prompt}

def main():
    parser = argparse.ArgumentParser(description="QLoRA Fine-Tuning for MindBridge AI")
    parser.add_argument("--config", type=str, default="./configs/qlora_config.json", help="Path to config file")
    args = parser.parse_args()
    
    config = load_config(args.config)
    print(f"Loading model: {config['model_name_or_path']}")
    
    # 1. Load Dataset
    print("Loading datasets...")
    train_dataset = load_dataset("json", data_files=config["dataset_path"], split="train")
    eval_dataset = load_dataset("json", data_files=config["eval_dataset_path"], split="train")
    
    # 2. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config["model_name_or_path"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Apply Chat Template Formatting
    train_dataset = train_dataset.map(lambda x: format_prompt(x, tokenizer))
    eval_dataset = eval_dataset.map(lambda x: format_prompt(x, tokenizer))
    
    # 3. Configure 4-bit Quantization (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
    
    # 4. Load Base Model
    print("Loading quantized base model...")
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name_or_path"],
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model.config.use_cache = False
    
    # Prepare model for PEFT
    model = prepare_model_for_kbit_training(model)
    
    # 5. Configure & Apply LoRA Adapter manually
    lora_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    print("Applying LoRA adapter manually...")
    model = get_peft_model(model, lora_config)
    
    # Explicitly force all trainable parameter weights to float32.
    # This prevents BFloat16 tensors from entering the optimizer and crashing GradScaler.
    for name, param in model.named_parameters():
        if param.requires_grad:
            param.data = param.data.to(torch.float32)
            
    print(f"Trainable Parameters: {model.print_trainable_parameters()}")
    
    # 6. Setup SFT Configuration (mixed precision fp16 enabled for accelerated T4 training)
    training_args = SFTConfig(
        output_dir=config["output_dir"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        learning_rate=config["learning_rate"],
        num_train_epochs=config["num_train_epochs"],
        weight_decay=config["weight_decay"],
        warmup_steps=10,
        logging_steps=config["logging_steps"],
        eval_strategy=config["eval_strategy"],
        eval_steps=config["eval_steps"],
        save_strategy="steps",
        save_steps=config["save_steps"],
        optim="paged_adamw_8bit",
        fp16=True,
        bf16=False,
        report_to="none",
        dataset_text_field="text",
        max_length=config["max_seq_length"]
    )
    
    # 7. Initialize Trainer (peft_config=None since we already wrapped the model manually)
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=None,
        processing_class=tokenizer,
        args=training_args,
    )
    
    # 8. Start Training
    print("Starting QLoRA Fine-tuning...")
    trainer.train()
    
    # 9. Save Adapter and Tokenizer
    print(f"Saving final adapter to {config['output_dir']}...")
    trainer.model.save_pretrained(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])
    
    # Save a clean adapter_config and model reference
    with open(Path(config["output_dir"]) / "README.md", "w") as f:
        f.write(f"# MindBridge Fine-Tuned LLM\n")
        f.write(f"Base Model: {config['model_name_or_path']}\n")
        f.write(f"Training approach: QLoRA\n")
        f.write(f"Use PeftModel.from_pretrained to load this adapter over the base model.\n")
        
    print("Training complete!")

if __name__ == "__main__":
    main()

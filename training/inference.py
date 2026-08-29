import torch
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

def load_model(base_model_name: str, adapter_path: str):
    print(f"Loading tokenizer from {base_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    print("Loading quantized base model...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    print(f"Loading LoRA adapter from {adapter_path}...")
    model = PeftModel.from_pretrained(base_model, adapter_path)
    
    return model, tokenizer

def generate_response(model, tokenizer, prompt_text: str):
    messages = [
        {"role": "system", "content": "You are a helpful, empathetic, and professional mental health assistant. Provide concise and directly relevant advice."},
        {"role": "user", "content": prompt_text}
    ]
    
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    print("Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=300, 
            temperature=0.6,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
    generated_text = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    return generated_text.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct")
    parser.add_argument("--adapter", type=str, default="./models/mindbridge-llm")
    args = parser.parse_args()
    
    model, tokenizer = load_model(args.base_model, args.adapter)
    
    print("\n================ MindBridge AI Interactive Test ================")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        response = generate_response(model, tokenizer, user_input)
        print(f"\nMindBridge AI: {response}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()

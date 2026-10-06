"""Test model loading with CUDA pre-init"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import torch
torch.cuda.init()
torch.cuda.empty_cache()

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

print("Step 1: CUDA ready")
print("Step 2: Loading tokenizer...")
tok = AutoTokenizer.from_pretrained(
    "model/Qwen/Qwen2___5-7B-Instruct", trust_remote_code=True
)
print("OK")

print("Step 3: Loading model 4-bit...")
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
    "model/Qwen/Qwen2___5-7B-Instruct",
    quantization_config=bnb,
    device_map="auto",
    trust_remote_code=True,
    dtype=torch.float16,
)
print(f"OK, VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

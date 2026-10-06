"""
独立的 LoRA 训练脚本
先关掉 start.bat，再运行这个脚本
"""
import os, sys, json, gc

# 先加载训练相关库（必须在 torch/CUDA 之前）
from datasets import Dataset
from transformers import TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


def main():
    print("=" * 50)
    print("加载模型 (4-bit)...")
    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
    )
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, quantization_config=bnb, device_map="auto",
        trust_remote_code=True, dtype=torch.float16,
    )

    print(f"模型加载完成，显存: {torch.cuda.memory_allocated()/1e9:.1f} GB")

    # LoRA
    print("注入 LoRA...")
    lora_cfg = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, target_modules=TARGET_MODULES,
        lora_dropout=LORA_DROPOUT, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_cfg)
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    model.print_trainable_parameters()

    # 加载数据
    data_path = os.path.join(DATA_DIR, "train_data.json")
    if not os.path.exists(data_path):
        print(f"[错误] 训练数据不存在: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    texts = []
    for item in raw:
        if isinstance(item, dict) and "instruction" in item and "output" in item:
            text = tok.apply_chat_template([
                {"role": "user", "content": item["instruction"]},
                {"role": "assistant", "content": item["output"]},
            ], tokenize=False)
            texts.append(text)

    print(f"训练样本: {len(texts)} 条")
    if len(texts) < 3:
        print("样本不足，再多聊一些吧")
        return

    enc = tok(texts, truncation=True, max_length=1024, padding="max_length", return_tensors="pt")
    dataset = Dataset.from_dict({
        "input_ids": enc["input_ids"],
        "attention_mask": enc["attention_mask"],
        "labels": enc["input_ids"].clone(),
    })

    epochs = max(3, min(10, 60 // len(texts)))
    print(f"训练轮数: {epochs}")

    args = TrainingArguments(
        output_dir=LORA_OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=epochs,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=5,
        save_steps=9999,
        save_total_limit=1,
        report_to="none",
        gradient_checkpointing=True,
        optim="adamw_torch",
        lr_scheduler_type="constant",
        warmup_steps=10,
        max_grad_norm=0.3,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        data_collator=DataCollatorForSeq2Seq(tok, pad_to_multiple_of=8),
    )

    print("开始训练...")
    trainer.train()

    print(f"保存到 {LORA_OUTPUT_DIR}")
    model.save_pretrained(LORA_OUTPUT_DIR)
    tok.save_pretrained(LORA_OUTPUT_DIR)
    print("训练完成！")


if __name__ == "__main__":
    main()

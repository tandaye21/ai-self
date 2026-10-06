import os

# ===== 路径配置 =====
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "Qwen", "Qwen2___5-7B-Instruct")
LORA_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "lora_output")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "memory")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# 本地资源路径（含个人桌面路径，不提交到仓库；在项目根目录建 config_local.py 覆盖即可）
ASSETS_DIR = ""
try:
    from config_local import ASSETS_DIR as _LOCAL_ASSETS_DIR
    ASSETS_DIR = _LOCAL_ASSETS_DIR
except ImportError:
    pass

# ===== 模型配置 =====
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
USE_4BIT = True
BNB_4BIT_COMPUTE_DTYPE = "float16"  # float16 / bfloat16
BNB_4BIT_QUANT_TYPE = "nf4"  # nf4 / fp4

# ===== LoRA 训练配置 =====
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

TRAINING_CONFIG = {
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 4,
    "num_train_epochs": 3,
    "learning_rate": 2e-4,
    "fp16": True,
    "logging_steps": 10,
    "save_steps": 50,
    "save_total_limit": 2,
    "max_grad_norm": 0.3,
    "warmup_ratio": 0.03,
    "lr_scheduler_type": "constant",
}

# ===== 记忆模块配置 =====
MEMORY_COLLECTION_NAME = "personal_memories"
TOP_K_MEMORIES = 3
MEMORY_SUMMARY_MAX_LENGTH = 200

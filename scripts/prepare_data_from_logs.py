"""
从聊天日志自动生成 LoRA 训练数据
你只需要每天聊天，这个脚本会把聊天记录转成训练格式
"""
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOG_DIR, DATA_DIR


def load_logs(days_back=None):
    """加载近期聊天日志"""
    all_records = []
    log_files = sorted(os.listdir(LOG_DIR), reverse=True)

    for fname in log_files:
        if not fname.endswith(".jsonl"):
            continue

        # 如果指定了天数，跳过旧文件
        if days_back:
            date_str = fname.replace(".jsonl", "")
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if (datetime.now() - file_date) > timedelta(days=days_back):
                    continue
            except:
                pass

        fpath = os.path.join(LOG_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_records.append(json.loads(line))

    return all_records


def is_high_quality(msg):
    """判断对话质量（简单的启发式过滤）"""
    user_msg = msg.get("user", "")
    assistant_msg = msg.get("assistant", "")

    # 过滤太短的回复
    if len(assistant_msg) < 10:
        return False

    # 过滤 "我不知道" 之类的无效回复
    useless = ["我不知道", "我不确定", "我不懂", "无法回答", "我不清楚"]
    if any(u in assistant_msg[:20] for u in useless):
        return False

    # 过滤太短的用户输入
    if len(user_msg) < 3:
        return False

    return True


def convert_to_training_format(records):
    """将聊天记录转为 LoRA 训练格式"""
    training_data = []
    seen = set()  # 去重

    for i, record in enumerate(records):
        if not is_high_quality(record):
            continue

        # 去重：用用户问题的 hash 做 key
        key = record["user"].strip()[:50]
        if key in seen:
            continue
        seen.add(key)

        training_data.append({
            "instruction": record["user"].strip(),
            "output": record["assistant"].strip(),
        })

    return training_data


def merge_with_existing(new_data):
    """合并到已有训练数据，避免重复"""
    existing_path = os.path.join(DATA_DIR, "train_data.json")
    existing = []

    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    # 去重合并
    seen_questions = set()
    for item in existing:
        q = item.get("instruction", "")[:50]
        seen_questions.add(q)

    for item in new_data:
        q = item.get("instruction", "")[:50]
        if q not in seen_questions:
            existing.append(item)
            seen_questions.add(q)

    return existing


def main():
    print("=" * 50)
    print("从聊天日志生成训练数据")
    print("=" * 50)

    # 加载最近 30 天的日志
    print("[1/3] 读取聊天日志...")
    logs = load_logs(days_back=30)
    print(f"      共找到 {len(logs)} 条对话记录")

    # 转换为训练格式
    print("[2/3] 筛选高质量对话...")
    training_data = convert_to_training_format(logs)
    print(f"      筛选出 {len(training_data)} 条可用的训练样本")

    if len(training_data) == 0:
        print("[提示] 没有找到可用的对话。先多聊一些吧！")
        return

    # 合并到已有数据
    print("[3/3] 合并到训练数据集...")
    merged = merge_with_existing(training_data)

    output_path = os.path.join(DATA_DIR, "train_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"      训练数据已保存到: {output_path}")
    print(f"      当前共 {len(merged)} 条样本")
    print()
    print("现在运行训练: python scripts/train_lora.py")


if __name__ == "__main__":
    main()

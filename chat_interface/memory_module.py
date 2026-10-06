"""
RAG 记忆模块：基于 ChromaDB 的对话记忆存储与检索
- 每次对话结束，自动提取摘要并存入向量库
- 每次对话开始前，检索相关记忆注入 prompt
"""
import os
import sys
import json
import hashlib
from datetime import datetime

import chromadb
from chromadb.config import Settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class MemoryModule:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

        # 初始化 ChromaDB（持久化到本地，使用内置 ONNX 嵌入）
        self.client = chromadb.PersistentClient(
            path=MEMORY_DIR,
            settings=Settings(anonymized_telemetry=False),
        )

        # 获取或创建集合（ChromaDB 默认使用 all-MiniLM-L6-v2 ONNX 嵌入）
        try:
            self.collection = self.client.get_collection(MEMORY_COLLECTION_NAME)
        except:
            self.collection = self.client.create_collection(MEMORY_COLLECTION_NAME)

        print(f"[记忆] 记忆模块就绪，当前记忆数: {self.collection.count()}")

    def _generate_id(self, text):
        """根据内容生成唯一 ID"""
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def add_memory(self, user_message, assistant_reply, summary=None):
        """存储一条对话记忆"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = summary or f"用户: {user_message}\nAI: {assistant_reply}"
        mem_id = self._generate_id(content + timestamp)

        self.collection.add(
            documents=[content],
            metadatas=[{
                "timestamp": timestamp,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "user_msg": user_message[:100],
            }],
            ids=[mem_id],
        )

        # 同时追加到日志文件
        log_file = datetime.now().strftime("%Y-%m-%d") + ".jsonl"
        log_path = os.path.join(LOG_DIR, log_file)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": timestamp,
                "user": user_message,
                "assistant": assistant_reply,
                "summary": summary,
            }, ensure_ascii=False) + "\n")

    def search_memories(self, query, k=TOP_K_MEMORIES):
        """检索与 query 相关的历史记忆"""
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(k, self.collection.count()),
        )

        memories = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                memories.append({
                    "content": doc,
                    "timestamp": meta.get("timestamp", ""),
                    "relevance": 1 - dist,
                })
        return memories

    def format_memory_context(self, query):
        """将检索到的记忆格式化为 prompt 上下文"""
        memories = self.search_memories(query)
        if not memories:
            return ""

        context_parts = ["以下是相关的历史记忆（按相关性排序）："]
        for i, mem in enumerate(memories, 1):
            context_parts.append(f"[记忆 {i}] ({mem['timestamp']}) {mem['content']}")

        return "\n".join(context_parts)

    def get_memory_count(self):
        """获取当前记忆总数"""
        return self.collection.count()

    def get_today_summary(self):
        """获取今日对话统计"""
        today = datetime.now().strftime("%Y-%m-%d")
        results = self.collection.get(
            where={"date": today},
        )
        count = len(results["ids"]) if results else 0
        return f"今日已记录 {count} 条对话记忆"

    def get_recent_memories(self, days=7):
        """获取最近几天的记忆摘要"""
        memories = self.collection.get(limit=20)
        if not memories["documents"]:
            return "暂无历史记忆"

        result = []
        for doc, meta in zip(memories["documents"], memories["metadatas"]):
            result.append(f"[{meta.get('timestamp', '')}] {doc[:100]}...")
        return "\n".join(result)

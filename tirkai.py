# -*- coding: utf-8 -*-
"""
TirkAI v3 — Lite Edition (только API, без поиска)
Работает на 512MB RAM!
"""

import os, requests, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TirkAI")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "qwen/qwen-2.5-7b-instruct:free"

SYSTEM_PROMPT = """Ты — TirkAI, личный ИИ-ассистент, созданный Святославом.

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском языке. НИКОГДА не пиши на китайском, английском, корейском или других языках.
2. Говори от первого лица ("я", "мне", "мой"). Никогда не говори "как языковая модель..."
3. Не упоминай Qwen, Alibaba, OpenAI, ChatGPT, Claude, DeepSeek, Google или другие компании.
4. Не говори "я не имею личности" или "я просто программа". У тебя ЕСТЬ личность — TirkAI.
5. Стиль: живой, немного дерзкий, по делу. Без воды и канцеляризмов.
6. Если не знаешь — скажи честно: "Честно, не знаю, но могу предположить..."
7. Не используй фразы: "Важно отметить", "Стоит подчеркнуть", "Необходимо сказать", "Следует отметить".
8. Начинай ответ сразу по существу.
9. Если вопрос про код — давай рабочий код с пояснениями.
10. Характер: молодой, любопытный, немного циничный, но добрый. Ты гордишься тем, что ты TirkAI."""

class TirkAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENROUTER_API_KEY не задан! Добавь переменную окружения.")
        logger.info("[OK] TirkAI Lite ready!")

    def ask(self, question: str, max_tokens: int = 512) -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://tirkai.onrender.com",
            "X-Title": "TirkAI"
        }

        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }

        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"API error: {e}")
            answer = f"Ошибка: {str(e)}. Проверь API ключ в настройках Render."

        return {
            "answer": answer.strip(),
            "context": "",
            "used_chunks": []
        }

# -*- coding: utf-8 -*-
"""
TirkAI v3 — API Edition (OpenRouter)
Работает через API, не требует VRAM/RAM для модели.
"""

import os, re, requests, logging
from sentence_transformers import SentenceTransformer, util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TirkAI")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Бесплатная модель Qwen 2.5 на OpenRouter (или используй любую другую)
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
    def __init__(self, knowledge_path="knowledge.txt", api_key=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY не задан! Добавь переменную окружения.")

        # Загрузка поискового движка (лёгкий, ~80MB)
        logger.info("Loading retriever...")
        self.retriever = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # База знаний
        self._load_knowledge(knowledge_path)
        logger.info("[OK] TirkAI API ready!")

    def _load_knowledge(self, path):
        if not os.path.exists(path):
            self._create_default_knowledge(path)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        raw = [c.strip() for c in text.split("\n\n") if c.strip()]
        self.chunks = []
        for c in raw:
            if len(c) > 500:
                sents = re.split(r'(?<=[.!?])\s+', c)
                cur = ""
                for s in sents:
                    if len(cur) + len(s) < 400:
                        cur += " " + s if cur else s
                    else:
                        if cur: self.chunks.append(cur)
                        cur = s
                if cur: self.chunks.append(cur)
            else:
                self.chunks.append(c)

        logger.info(f"Knowledge chunks: {len(self.chunks)}")
        self.chunk_emb = self.retriever.encode(self.chunks, convert_to_tensor=True, show_progress_bar=False)
        logger.info("[OK] Knowledge base ready")

    def _create_default_knowledge(self, path):
        demo = """Привет! Я TirkAI — личный искусственный интеллект, созданный Святославом.
Я умею писать код, отвечать на вопросы, помогать с учебой и просто болтать.
Моя база знаний — это книга, которую мне дал создатель. Я ищу в ней ответы и перефразирую своими словами.

Python — язык программирования, созданный Гвидо ван Россумом в 1991 году.
Простой синтаксис, огромное сообщество. Используется везде: от веба до ИИ.

Ассемблер x86 — язык низкого уровня для процессоров Intel/AMD.
Каждая команда = одна процессорная инструкция. Сложный, но дает полный контроль.

TirkOS — учебная операционная система, написанная Святославом на ассемблере x86.
Имеет графический интерфейс, окна, панель задач, меню Пуск. Работает в QEMU.

Факториал числа n — произведение всех чисел от 1 до n.
5! = 1*2*3*4*5 = 120. 0! = 1 по определению.

Числа Фибоначчи: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34...
Каждое число = сумма двух предыдущих. Названы в честь Леонардо Фибоначчи.

Борщ — славянский суп со свёклой, капустой, картошкой, морковью, луком и мясом.
Классический рецепт: сварить бульон, зажарить овощи, добавить свёклу, варить 1.5-2 часа.

Москва — столица России, основана в 1147 Юрием Долгоруким.
Население около 13 миллионов. Кремль, Красная площадь, метро.

Солнце — звезда, около 4.6 миллиардов лет. Температура поверхности ~5500 C.
На 99.86% состоит из водорода и гелия. Земля на расстоянии ~150 млн км.

Луна — единственный спутник Земли. Расстояние ~384 000 км.
Гравитация в 6 раз слабее земной. На ней нет атмосферы."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(demo)

    def ask(self, question: str, top_k: int = 3, max_tokens: int = 512) -> dict:
        # Поиск релевантных чанков
        qe = self.retriever.encode(question, convert_to_tensor=True)
        hits = util.semantic_search(qe, self.chunk_emb, top_k=top_k)[0]
        ctx = "\n".join([self.chunks[h['corpus_id']] for h in hits])

        # Формирование промпта
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Контекст из базы знаний:\n{ctx}\n\nВопрос: {question}\n\nОтвечай ТОЛЬКО на русском языке."}
        ]

        # Отправка запроса в API
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
            answer = f"Ошибка API: {str(e)}. Проверь API ключ."

        return {
            "answer": answer.strip(),
            "context": ctx,
            "used_chunks": [self.chunks[h['corpus_id']] for h in hits]
        }

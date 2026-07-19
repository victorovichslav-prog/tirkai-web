# -*- coding: utf-8 -*-
"""
TirkAI v2 — Server Edition
Ядро ИИ-ассистента для веб-сервера.
"""

import os, re, torch, logging
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TirkAI")

# ─── СИСТЕМНЫЙ ПРОМПТ ───────────────────────────────────────────────────────
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

# ─── КЛАСС TIRKAI ──────────────────────────────────────────────────────────
class TirkAI:
    def __init__(self, knowledge_path="knowledge.txt"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Device: {self.device.upper()}")

        # Загрузка поискового движка
        logger.info("Loading retriever...")
        self.retriever = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Загрузка LLM
        logger.info("Loading Qwen 7B...")
        MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

        if self.device == "cuda":
            bnb = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
            self.tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
            self.llm = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                quantization_config=bnb,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
        else:
            # CPU mode — загружаем в 8-bit для экономии RAM
            self.tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
            self.llm = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                load_in_8bit=True if torch.cuda.is_available() else False,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                torch_dtype=torch.float32
            )
            if not torch.cuda.is_available():
                self.llm = self.llm.to("cpu")

        logger.info("[OK] LLM loaded")

        # База знаний
        self._load_knowledge(knowledge_path)

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

        prompt = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tok(prompt, return_tensors="pt").to(self.llm.device)

        # Генерация
        with torch.no_grad():
            out = self.llm.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tok.eos_token_id
            )

        resp = self.tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

        return {
            "answer": resp.strip(),
            "context": ctx,
            "used_chunks": [self.chunks[h['corpus_id']] for h in hits]
        }

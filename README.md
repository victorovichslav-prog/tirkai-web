# 🧠 TirkAI Web

Личный ИИ-ассистент на Qwen2.5-7B с веб-интерфейсом.

## 📁 Структура

```
tirkai-site/
├── app.py              # FastAPI сервер
├── tirkai.py           # Ядро TirkAI
├── knowledge.txt       # База знаний (замени на свою!)
├── requirements.txt    # Зависимости
├── Dockerfile          # Для Render
├── render.yaml         # Конфиг Render
├── static/style.css    # Стили
└── templates/index.html # Веб-интерфейс
```

## 🚀 Запуск локально

```bash
pip install -r requirements.txt
python app.py
```

Открой http://localhost:8000

## 🌐 Деплой на Render

### 1. Создай репозиторий на GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ТВОЙ_НИК/tirkai-web.git
git push -u origin main
```

### 2. На Render.com:
1. New → Web Service
2. Подключи GitHub репо
3. Runtime: Docker
4. Plan: **Standard** (нужен для 7B модели, минимум 4GB RAM)
   - Или **Starter** (бесплатно, но модель загрузится в 8-bit и будет медленнее)
5. Environment Variables добавь:
   - `TRANSFORMERS_CACHE` = `/tmp/huggingface`
   - `HF_HOME` = `/tmp/huggingface`
6. Deploy!

### 3. Замени knowledge.txt
Замени файл `knowledge.txt` на свою базу знаний. Формат:
```
Заголовок темы

Текст знания. Можно несколько абзацев.

Следующая тема

Ещё текст...
```

## ⚠️ Важно

- **Qwen 7B в 4-bit** требует ~4GB VRAM (GPU) или ~8GB RAM (CPU)
- На Render бесплатный план (Starter) даёт 512MB RAM — **недостаточно** для 7B
- Нужен минимум **Standard** план (2GB RAM) или лучше **Pro** (4GB+)
- Альтернатива: используй меньшую модель (Qwen2.5-1.5B или 3B) — измени `MODEL_NAME` в `tirkai.py`

## 🔧 Альтернативные модели (если не хватает RAM)

В `tirkai.py` замени:
```python
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # ~1.5GB RAM
# или
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"    # ~3GB RAM
```

## 📄 Лицензия

Твой проект, делай что хочешь 🔥

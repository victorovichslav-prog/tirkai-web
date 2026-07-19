FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаём knowledge.txt если его нет (tirkai.py создаст дефолтный)
# Но лучше иметь свой — замени на свой файл

# Порт
EXPOSE 8000

# Запуск
CMD ["python", "app.py"]

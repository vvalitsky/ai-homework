FROM python:3.11-slim

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установить рабочую директорию
WORKDIR /app

# Скопировать requirements.txt
COPY requirements.txt .

# Upgrade pip and install Python зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Скопировать весь проект
COPY . .

# Убедиться, что индекс скопирован в правильное место
RUN if [ -d "Task3/index_output" ]; then \
        cp -r Task3/index_output /app/index_output; \
    fi

# Открыть порт для REST API
EXPOSE 8000

# Здоровье-check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Установить переменные окружения для путей
ENV INDEX_DIR=/app/index_output
ENV PYTHONUNBUFFERED=1

# Команда по умолчанию - запуск REST API
CMD ["python3", "Task4/rag_api.py"]

#!/usr/bin/env python3
"""
REST API для RAG-бота используя FastAPI

Позволяет взаимодействовать с RAG-ботом через HTTP requests.
"""

import os
import sys
import logging
from typing import List, Optional
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Добавить Task4 и родительскую директорию в sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

# Импортировать RAG-бот
from rag_bot import RAGBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализировать FastAPI
app = FastAPI(
    title="RAG Bot API",
    description="API для взаимодействия с RAG-ботом на основе FAISS и LLM",
    version="1.0.0"
)

# Инициализировать RAG-бот
def init_bot():
    """Инициализировать RAG-бот с правильными путями."""
    try:
        # Попробовать разные пути для локального запуска и Docker
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

        possible_paths = [
            os.path.join(project_root, "Task3", "index_output"),  # Абсолютный путь из Task4/
            os.path.join(os.getcwd(), "Task3", "index_output"),   # Относительный из текущей директории
            "/app/index_output",       # Docker путь
            os.environ.get("INDEX_DIR", ""),  # Переменная окружения
        ]

        for index_dir in possible_paths:
            if index_dir and os.path.exists(os.path.join(index_dir, "faiss.index")):
                logger.info(f"Найден индекс: {index_dir}")
                return RAGBot(index_dir=index_dir)

        logger.error("FAISS индекс не найден ни по одному пути")
        logger.error(f"Проверены пути: {possible_paths}")
        return None
    except Exception as e:
        logger.error(f"Ошибка инициализации RAG-бота: {e}")
        import traceback
        traceback.print_exc()
        return None

bot = init_bot()
if bot:
    logger.info("✓ RAG-бот успешно инициализирован")
else:
    logger.warning("⚠ RAG-бот не инициализирован")


# Pydantic модели
class QueryRequest(BaseModel):
    """Запрос к боту."""
    question: str
    top_k: int = 3
    use_llm: bool = False


class DocumentResult(BaseModel):
    """Результат документа."""
    text: str
    source: str
    title: str
    distance: float


class QueryResponse(BaseModel):
    """Ответ на запрос."""
    question: str
    context: List[DocumentResult]
    prompt: str
    answer: Optional[str] = None
    status: str


@app.get("/")
async def root():
    """Главная страница API."""
    return {
        "message": "RAG Bot API",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST запрос к боту",
            "/health": "Проверка состояния",
            "/docs": "SwaggerUI документация"
        }
    }


@app.get("/health")
async def health():
    """Проверка состояния API."""
    if bot is None:
        return {
            "status": "INITIALIZING",
            "bot_initialized": False,
            "message": "RAG Bot индекс еще не загружен. Пожалуйста, выполните Task 3."
        }

    return {
        "status": "OK",
        "bot_initialized": True,
        "chunks_count": bot.retriever.info.get("total_chunks", 0),
        "embedding_model": bot.retriever.info.get("embedding_model", "unknown")
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Получить ответ на вопрос.

    Query example:
    ```json
    {
        "question": "Кто такой Каелин Скайфайер?",
        "top_k": 3,
        "use_llm": false
    }
    ```
    """
    if bot is None:
        raise HTTPException(status_code=503, detail="RAG Bot индекс еще не загружен. Выполните Task 3 для построения индекса.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустой")

    try:
        result = bot.answer(
            question=request.question,
            top_k=request.top_k,
            use_llm=request.use_llm
        )

        return QueryResponse(
            question=result["question"],
            context=result["context"],
            prompt=result["prompt"],
            answer=result.get("answer"),
            status="success"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info")
async def info():
    """Информация об индексе."""
    if bot is None:
        raise HTTPException(status_code=503, detail="RAG Bot не инициализирован")

    return {
        "index_info": bot.retriever.info,
        "examples": bot.EXAMPLES,
    }


def main():
    """Запустить API сервер."""
    import sys

    if bot is None:
        print("⚠️  RAG-бот не инициализирован - запуск API в режиме демонстрации")
        print("Индекс FAISS еще не загружен. Постройте индекс с помощью Task 3.")
        print()

    print("\n" + "="*60)
    print("RAG Bot REST API")
    print("="*60)
    print("\nЗапуск сервера на http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    print("="*60 + "\n")

    # Запустить сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

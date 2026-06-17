#!/usr/bin/env python3
"""
Задание 4: RAG-бот с техниками промптинга (Few-shot и Chain-of-Thought)

Реализует полный RAG пайплайн с:
- Поиском релевантных чанков в FAISS индексе
- Few-shot промптингом (примеры в контексте)
- Chain-of-Thought (объяснение шагов рассуждения)
- Интеграцией с LLM (OpenAI, YandexGPT или локальная модель)
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict
import logging

# Установить логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Попытаться импортировать зав iс имости
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
except ImportError as e:
    logger.error(f"Required package missing: {e}")
    logger.error("Please install: pip install sentence-transformers faiss-cpu")
    sys.exit(1)


class RAGRetriever:
    """Компонент поиска релевантных документов."""

    def __init__(self, index_dir: Optional[str] = None):
        """Загрузить индекс и модель эмбеддингов."""
        # Если не указан, попробовать переменную окружения или использовать по умолчанию
        if index_dir is None:
            index_dir = os.environ.get("INDEX_DIR", "../Task3/index_output")

        self.index_dir = index_dir

        # Загрузить информацию об индексе
        info_path = os.path.join(index_dir, "index_info.json")
        with open(info_path, 'r') as f:
            self.info = json.load(f)

        # Загрузить модель эмбеддингов
        logger.info("Загрузка модели эмбеддингов...")
        self.model = SentenceTransformer(self.info["embedding_model"])

        # Загрузить FAISS индекс
        logger.info("Загрузка FAISS индекса...")
        index_path = os.path.join(index_dir, "faiss.index")
        self.index = faiss.read_index(index_path)

        # Загрузить чанки
        logger.info("Загрузка чанков.....")
        chunks_path = os.path.join(index_dir, "chunks.json")
        with open(chunks_path, 'r') as f:
            self.chunks = json.load(f)

        logger.info(f"✓ RAG Retriever инициализирован ({self.info['total_chunks']} чанков)")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Найти top_k наиболее релевантных документов для запроса."""
        # Получить эмбеддинг запроса
        query_embedding = self.model.encode([query], show_progress_bar=False).astype('float32')

        # Найти k ближайших векторов
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "title": chunk["title"],
                "distance": float(distance),
            })

        return results


class RAGBot:
    """Основной RAG-бот с Chain-of-Thought и Few-shot промптингом."""

    # Few-shot примеры из базы знаний
    EXAMPLES = [
        {
            "question": "Опишите, кого называли Сагом Проводником Пустоты?",
            "answer": "Сага Проводника Пустоты также знали как Зоры. Это был старейший и мудрейший из Пустотных Дозорников."
        },
        {
            "question": "Какова была цель Вакуум Ядра?",
            "answer": "Вакуум Ядро был создан Вакуумным Порядком как мобильная станция, способная уничтожить целые планеты. Это была их величайшее оружие в войне против Свободного Альянса."
        }
    ]

    # System промпт с Chain-of-Thought
    SYSTEM_PROMPT = """Ты помощник, который помогает людям найти информацию в корпоративной базе знаний.

ВАЖНО: Следуй этим правилам:
1. Всегда сначала ДУМАЙ и ОБЪЯСНЯЙ свои шаги логически
2. Используй информацию ТОЛЬКО из предоставленного контекста
3. Если информации нет в контексте, честно скажи "Я не знаю"
4. Приводи источники (из каких документов взята информация)
5. Будь точен и конкретен в ответах

Формат ответа:
1. ДУМАЮ: [объясни, как ты будешь решать этот вопрос]
2. ИЩУ: [какую информацию нужно найти]
3. НАШЁЛ: [что ты нашёл в контексте]
4. ОТВЕТ: [итоговый ответ с кавычками из контекста или признай, что не знаешь]
5. ИСТОЧНИКИ: [укажи, из какие документов была информация]"""

    def __init__(self, index_dir: Optional[str] = None):
        """Инициализировать RAG-бот."""
        # Если не указан, попробовать переменную окружения
        if index_dir is None:
            index_dir = os.environ.get("INDEX_DIR", "../Task3/index_output")
        self.retriever = RAGRetriever(index_dir)

    def create_prompt(self, question: str, context: List[Dict]) -> str:
        """Создать промпт с Few-shot примерами и контекстом."""

        # Few-shot примеры
        few_shot_text = "ПРИМЕРЫ ОТВЕТОВ:\n"
        for i, example in enumerate(self.EXAMPLES, 1):
            few_shot_text += f"\nПример {i}:\n"
            few_shot_text += f"Q: {example['question']}\n"
            few_shot_text += f"A: {example['answer']}\n"

        # Контекст из найденных документов
        context_text = "КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:\n"
        for i, doc in enumerate(context, 1):
            context_text += f"\n[Документ {i}: {doc['source']}]\n"
            context_text += f"Тема: {doc['title']}\n"
            context_text += f"Содержание: {doc['text']}\n"
            context_text += f"---\n"

        # Финальный запрос
        prompt = f"""{few_shot_text}

{context_text}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {question}

Ответь, следуя правилам из System Prompt."""

        return prompt

    def answer(self, question: str, top_k: int = 3, use_llm: bool = False) -> Dict:
        """
        Получить ответ на вопрос.

        Args:
            question: Вопрос пользователя
            top_k: Количество документов для поиска
            use_llm: Использовать ли LLM для генерации ответа или вернуть составленный промпт

        Returns:
            {
                "question": вопрос,
                "context": найденные документы,
                "prompt": созданный промпт,
                "answer": ответ LLM (если use_llm=True)
            }
        """
        logger.info(f"Обработка вопроса: {question}")

        # Поиск контекста
        context = self.retriever.retrieve(question, top_k=top_k)

        if not context:
            logger.warning("Контекст не найден")
            return {
                "question": question,
                "context": [],
                "prompt": "Контекст не найден",
                "answer": "Я не имею достаточно информации в базе знаний, чтобы ответить на этот вопрос."
            }

        # Создать промпт
        prompt = self.create_prompt(question, context)

        logger.info(f"Найдено {len(context)} документов")

        result = {
            "question": question,
            "context": context,
            "prompt": prompt,
        }

        if use_llm:
            # Здесь должна быть интеграция с LLM (OpenAI, YandexGPT или локальная модель)
            # Пока показываем, как это бы выглядело
            logger.info("LLM интиеграция не реализована в демо версии")
            result["note"] = "Для полной функциональности нужна интеграция с LLM API"

        return result

    def interactive_mode(self):
        """Интерактивный режим чата."""
        print("\n" + "="*60)
        print("RAG-БОТ - Интерактивный режим")
        print("="*60)
        print("Введите вопрос (или 'выход' для завершения):\n")

        while True:
            try:
                question = input("Вопрос: ").strip()

                if question.lower() in ['выход', 'exit', 'quit', 'q']:
                    print("\nДо свидания!")
                    break

                if not question:
                    continue

                # Получить ответ
                result = self.answer(question, top_k=3)

                # Вывести результаты
                print("\n" + "-"*60)
                print("НАЙДЕННЫЕ ИСТОЧНИКИ:")
                for i, doc in enumerate(result["context"], 1):
                    print(f"\n{i}. {doc['source']} ({doc['title']})")
                    print(f"   Текст: {doc['text'][:150]}...")

                print("\n" + "-"*60)
                print("СОЗДАННЫЙ ПРОМПТ (для демонстрации):")
                print(result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"])

                print("\n" + "-"*60)

            except KeyboardInterrupt:
                print("\n\nПрограмма прервана пользователем")
                break
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                print(f"Ошибка: {e}")


def main():
    """Главная функция."""
    import sys

    # Проверить наличие индекса
    index_dir = "../Task3/index_output"
    if not os.path.exists(os.path.join(index_dir, "faiss.index")):
        print("❌ FAISS индекс не найден")
        print("Пожалуйста, сначала выполните Task 3")
        sys.exit(1)

    try:
        # Инициализировать бот
        bot = RAGBot(index_dir)

        # Примеры запросов для демонстрации
        test_questions = [
            "Кто такой Каелин Скайфайер?",
            "Какова была цель Вакуум Ядра?",
            "Расскажи про Свободный Альянс",
        ]

        print("\n" + "="*60)
        print("Боевой RAG-БОТ - Задание 4")
        print("="*60)

        # Запустить демонстрацию
        for question in test_questions[:1]:
            print(f"\n📝 Вопрос: {question}\n")
            result = bot.answer(question, top_k=3)

            print(f"Найдено {len(result['context'])} релевантных документов:")
            for i, doc in enumerate(result['context'], 1):
                print(f"\n{i}. [{doc['source']}]")
                print(f"   Тема: {doc['title']}")
                print(f"   Отрывок: {doc['text'][:100]}...")

        print("\n" + "="*60)

        # Запустить интерактивный режим
        bot.interactive_mode()

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

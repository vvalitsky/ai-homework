#!/usr/bin/env python3
"""
Задание 7: Аналитика покрытия и качества базы знаний

Проводит автоматическое тестирование на "золотых" вопросах,
логирует процесс, выявляет пробелы в базе знаний.
"""

import os
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import csv

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("Please install: pip install sentence-transformers faiss-cpu numpy")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Оценивает качество RAG-системы."""

    def __init__(self, index_dir: Optional[str] = None):
        """Инициализировать оценщик."""
        if index_dir is None:
            script_dir = Path(__file__).parent.absolute()
            project_root = script_dir.parent
            index_dir = project_root / "Task3" / "index_output"
        else:
            index_dir = Path(index_dir)

        # Загрузить индекс
        logger.info(f"Загрузка FAISS индекса из {index_dir}...")
        index_path = index_dir / "faiss.index"
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS индекс не найден: {index_path}")
        self.index = faiss.read_index(str(index_path))

        # Загрузить чанки
        chunks_path = index_dir / "chunks.json"
        if not chunks_path.exists():
            raise FileNotFoundError(f"chunks.json не найден: {chunks_path}")
        with open(chunks_path, 'r') as f:
            self.chunks = json.load(f)

        # Загрузить информацию об индексе
        info_path = index_dir / "index_info.json"
        if not info_path.exists():
            raise FileNotFoundError(f"index_info.json не найден: {info_path}")
        with open(info_path, 'r') as f:
            self.info = json.load(f)

        # Инициализировать модель эмбеддингов
        logger.info("Загрузка модели эмбеддингов...")
        self.model = SentenceTransformer(self.info["embedding_model"])

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Сделать поиск в индексе."""
        query_embedding = self.model.encode([query], show_progress_bar=False).astype('float32')
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

    def evaluate_query(
        self,
        query: str,
        expected_keywords: Optional[List[str]] = None,
        top_k: int = 3
    ) -> Dict:
        """Оценить результаты поиска для одного запроса."""
        results = self.search(query, top_k=top_k)

        # Проверить, была ли найдена информация
        found = len(results) > 0 and results[0]["distance"] < 100  # FAISS расстояния

        # Если даны ключевые слова, проверить наличие первого результата
        accuracy = False
        if expected_keywords and found:
            combined_text = " ".join([r["text"] for r in results]).lower()
            accuracy = any(keyword.lower() in combined_text for keyword in expected_keywords)

        return {
            "query": query,
            "found": found,
            "results_count": len(results),
            "top_result_distance": results[0]["distance"] if results else None,
            "associated_keywords": expected_keywords or [],
            "accuracy": accuracy,
            "results": results,
        }


def create_golden_questions() -> List[Dict]:
    """Создать "золотой" набор вопросов для тестирования."""
    return [
        # Вопросы, на которые бот должен ответить (есть в базе)
        {
            "question": "Кто такой Каелин Скайфайер?",
            "keywords": ["Каелин", "Скайфайер", "Кайелин"],
            "should_answer": True,
        },
        {
            "question": "Какова была цель Вакуум Ядра?",
            "keywords": ["Вакуум", "Ядра", "уничтожить", "планеты"],
            "should_answer": True,
        },
        {
            "question": "Расскажи про Свободный Альянс",
            "keywords": ["Свободный", "Альянс", "Альянса"],
            "should_answer": True,
        },
        {
            "question": "Что такое Синтез Поток?",
            "keywords": ["Синтез", "Поток", "энергия", "живые"],
            "should_answer": True,
        },
        {
            "question": "Опишите Пустотные Дозорники",
            "keywords": ["Пустотные", "Дозорники", "Дозорники", "порядок"],
            "should_answer": True,
        },
        {
            "question": "Как работает Плазменный Клинок?",
            "keywords": ["Плазменный", "Клинок", "оружие", "лезвие"],
            "should_answer": True,
        },
        # Вопросы на удалённые/отсутствующие темы (бот не должен ответить)
        {
            "question": "Расскажи про неизвестную империю Абрадакабра",
            "keywords": ["Абრадакабра", "неизвестная"],
            "should_answer": False,
        },
        {
            "question": "Какова история планеты Несужествиум?",
            "keywords": ["Несужествиум"],
            "should_answer": False,
        },
        {
            "question": "Кто объявил войну Мегаимперии?",
            "keywords": ["Мегаимперии"],
            "should_answer": False,
        },
    ]


def generate_evaluation_report(results: List[Dict]) -> Dict:
    """Создать отчёт об оценке."""
    total_queries = len(results)
    successful_answers = sum(1 for r in results if r["found"])
    accurate_answers = sum(1 for r in results if r["accuracy"])

    should_answer_count = sum(1 for r in results if r.get("should_answer", True))
    shouldnt_answer_count = total_queries - should_answer_count

    correct_rejections = sum(
        1 for r in results
        if not r.get("should_answer", True) and not r["found"]
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": total_queries,
        "successful_answers": successful_answers,
        "successful_rate": successful_answers / total_queries if total_queries > 0 else 0,
        "accurate_answers": accurate_answers,
        "correct_rejections": correct_rejections,
        "queries_that_should_answer": should_answer_count,
        "queries_that_shouldnt_answer": shouldnt_answer_count,
        "recall": successful_answers / should_answer_count if should_answer_count > 0 else 0,
        "specificity": correct_rejections / shouldnt_answer_count if shouldnt_answer_count > 0 else 0,
        "details": results,
    }

    return report


def main():
    """Главная функция."""
    try:
        print("\n" + "=" * 60)
        print("Задание 7: Аналитика покрытия и качества базы знаний")
        print("=" * 60)

        # Инициализировать оценщик
        evaluator = RAGEvaluator()

        # Получить "золотые" вопросы
        golden_questions = create_golden_questions()

        print(f"\nТестирование на {len(golden_questions)} вопросах...")

        # Оценить каждый вопрос
        results = []
        for i, q_obj in enumerate(golden_questions, 1):
            query = q_obj["question"]
            keywords = q_obj.get("keywords", [])
            should_answer = q_obj.get("should_answer", True)

            print(f"\n[{i}/{len(golden_questions)}] {query}")

            result = evaluator.evaluate_query(
                query,
                expected_keywords=keywords,
                top_k=3
            )
            result["should_answer"] = should_answer

            # Вывести результат
            if result["found"]:
                print(f"  ✓ Найдено (distance: {result['top_result_distance']:.4f})")
                print(f"    Source: {result['results'][0]['source']}")
            else:
                print(f"  ✗ Не найдено")

            results.append(result)

        # Создать отчёт
        report = generate_evaluation_report(results)

        # Вывести статистику
        print("\n" + "=" * 60)
        print("ИТОГИ ОЦЕНКИ:")
        print("=" * 60)
        print(f"Успешных ответов: {report['successful_answers']}/{report['total_queries']}")
        print(f"Success rate: {report['successful_rate']:.2%}")
        print(f"Recall (найти то, что должно быть): {report['recall']:.2%}")
        print(f"Specificity (отклонить то, чего нет): {report['specificity']:.2%}")

        # Сохранить результаты в JSON
        with open("evaluation_report.json", 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\n✓ Отчёт сохранён в evaluation_report.json")

        # Сохранить в CSV для анализа
        with open("evaluation_results.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Query", "Found", "Distance", "Should Answer", "Accuracy"])
            for r in results:
                writer.writerow([
                    r["query"],
                    r["found"],
                    r["top_result_distance"],
                    r["should_answer"],
                    r["accuracy"],
                ])
        print("✓ Результаты сохранены в evaluation_results.csv")

        # Логирование запросов
        log_file = Path("query_logs.jsonl")
        with open(log_file, 'a') as f:
            for r in results:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "query": r["query"],
                    "found": r["found"],
                    "results_count": r["results_count"],
                    "top_distance": r["top_result_distance"],
                    "should_answer": r["should_answer"],
                    "accuracy": r["accuracy"],
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print("✓ Логи сохранены в query_logs.jsonl")

        print("\n" + "=" * 60)
        return report

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

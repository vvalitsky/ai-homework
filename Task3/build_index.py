#!/usr/bin/env python3
"""
Задание 3: Создание векторного индекса базы знаний

Скрипт преобразует документы из базы знаний в:
1. Чанки (chunks) - логически связанные фрагменты текста
2. Эмбеддинги (embeddings) - векторные представления
3. FAISS индекс - быстрый поиск по сходству
"""

import os
import json
import time
import sys
import warnings
from pathlib import Path
from typing import List, Dict, Tuple
import pickle

# Suppress the resource_tracker warning from loky - it's harmless cleanup
warnings.filterwarnings("ignore", category=UserWarning, message=".*resource_tracker.*")

# Disable multiprocessing before importing sentence_transformers
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['NUMEXPR_MAX_THREADS'] = '1'

# Проверим доступны ли необходимые библиотеки
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing sentence-transformers...")
    os.system("pip install sentence-transformers")
    from sentence_transformers import SentenceTransformer

try:
    import torch
    torch.set_num_threads(1)
except ImportError:
    pass

try:
    import faiss
except ImportError:
    print("Installing faiss-cpu...")
    os.system("pip install faiss-cpu")
    import faiss

import numpy as np


class DocumentChunker:
    """Разбивает документы на логические чанки."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Args:
            chunk_size: целевой размер чанка в токенах (примерно 4 символа = 1 токен)
            overlap: перекрытие между чанками в символах для контекста
        """
        self.chunk_size = chunk_size * 4  # конвертируем в символы
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Разбить текст на чанки с метаданными."""
        chunks = []
        text_length = len(text)
        chunk_id = 0

        start = 0
        while start < text_length:
            # Определить конец чанка
            end = min(start + self.chunk_size, text_length)

            # Если не конец документа, найти конец предложения
            if end < text_length:
                # Найти последний период, восклицательный или вопросительный знак
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                if sentence_end > start + self.chunk_size // 2:  # если разумно близко
                    end = sentence_end + 1

            chunk_text = text[start:end].strip()

            if chunk_text:  # только если основной текст
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "start_pos": start,
                    "end_pos": end,
                    "source": metadata.get("source", "unknown"),
                    "title": metadata.get("title", ""),
                })
                chunk_id += 1

            # Переместиться на следующий чанк с перекрытием
            start = max(end - self.overlap, start + 1)
            if start >= text_length:
                break

        return chunks


class KnowledgeBaseIndexer:
    """Создаёт и управляет FAISS индексом для базы знаний."""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Args:
            embedding_model: модель из HuggingFace для генерации эмбеддингов
        """
        self.embedding_model = embedding_model
        print("  Загрузка модели эмбеддингов (это может занять время)...")
        # Disable multiprocessing to avoid semaphore issues
        self.model = SentenceTransformer(embedding_model)
        # Set to single-threaded execution
        self.model.max_seq_length = 256
        try:
            self.embedding_dim = self.model.get_embedding_dimension()
        except AttributeError:
            # Fallback for older versions
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.chunks = []
        self.index = None
        self.embeddings = None

    def load_documents(self, docs_dir: str) -> List[Dict]:
        """Загрузить документы из директории."""
        docs = []
        docs_path = Path(docs_dir)

        for file_path in sorted(docs_path.glob("*.txt")):
            if file_path.name == "terms_map.json":
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Извлечь заголовок (первая строка с #)
            lines = content.split('\n')
            title = lines[0].replace('# ', '').strip() if lines[0].startswith('#') else "Unknown"

            # Получить основной текст
            text_content = '\n'.join(lines[1:]).strip()

            if text_content:
                docs.append({
                    "title": title,
                    "source": file_path.name,
                    "content": text_content,
                })

        print(f"✓ Загружено {len(docs)} документов")
        return docs

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Разбить документы на чанки."""
        chunker = DocumentChunker(chunk_size=500, overlap=100)
        all_chunks = []

        for doc in documents:
            chunks = chunker.chunk_text(
                doc["content"],
                {"source": doc["source"], "title": doc["title"]}
            )
            all_chunks.extend(chunks)

        print(f"✓ Создано {len(all_chunks)} чанков")
        self.chunks = all_chunks
        return all_chunks

    def generate_embeddings(self, batch_size: int = 32) -> np.ndarray:
        """Сгенерировать эмбеддинги для всех чанков."""
        chunk_texts = [chunk["text"] for chunk in self.chunks]

        print(f"Генерирование {len(chunk_texts)} эмбеддингов (это может занять время)...")
        start_time = time.time()

        # Генерировать эмбеддинги батчами - НЕ использовать параллелизм
        embeddings_list = []
        total_batches = (len(chunk_texts) + batch_size - 1) // batch_size

        for batch_num, i in enumerate(range(0, len(chunk_texts), batch_size)):
            batch = chunk_texts[i:i+batch_size]
            # Use single-threaded encoding with no parallelism
            batch_embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings_list.append(batch_embeddings)

            # Progress indicator every 10 batches
            if (batch_num + 1) % 10 == 0 or (batch_num + 1) == total_batches:
                pct = ((batch_num + 1) / total_batches) * 100
                print(f"  прогресс: {pct:.1f}% ({batch_num + 1}/{total_batches} батчей)")
                sys.stdout.flush()

        embeddings = np.vstack(embeddings_list).astype('float32')
        elapsed = time.time() - start_time

        print(f"✓ Эмбеддинги созданы за {elapsed:.2f} сек")
        print(f"  Размер эмбеддинга: {embeddings.shape[1]} измерений")
        print(f"  Всего векторов: {embeddings.shape[0]}")

        self.embeddings = embeddings
        return embeddings

    def build_index(self) -> faiss.IndexFlatL2:
        """Построить FAISS индекс."""
        if self.embeddings is None:
            raise ValueError("Embeddings not generated yet")

        # Используем IndexFlatL2 - простой индекс с L2 расстанием
        # Для большего масштаба можно использовать IndexIVFFlat или другие
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(self.embeddings)

        print(f"✓ FAISS индекс построен")
        print(f"  Векторов в индексе: {index.ntotal}")

        self.index = index
        return index

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Найти k наиболее релевантных чанков для запроса."""
        if self.index is None:
            raise ValueError("Index not built yet")

        # Получить эмбеддинг запроса
        query_embedding = self.model.encode([query], show_progress_bar=False).astype('float32')

        # Найти k ближайших соседей
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk["chunk_id"],
                "source": chunk["source"],
                "title": chunk["title"],
                "text": chunk["text"],
                "distance": float(distance),  # меньше = более релевантно
            })

        return results

    def save_index(self, output_dir: str = "index_output"):
        """Сохранить индекс, чанки и метаданные."""
        output_dir = os.path.abspath(output_dir)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Сохранить FAISS индекс
        faiss_path = os.path.join(output_dir, "faiss.index")
        faiss.write_index(self.index, faiss_path)

        # Сохранить чанки (текст и метаданные)
        chunks_path = os.path.join(output_dir, "chunks.json")
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

        # Сохранить информацию об индексе
        info = {
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dim,
            "total_chunks": len(self.chunks),
            "total_vectors": self.index.ntotal,
        }
        info_path = os.path.join(output_dir, "index_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        print(f"✓ Индекс сохранён в '{output_dir}/'")
        print(f"  - faiss.index ({os.path.getsize(faiss_path) / 1024:.1f} KB)")
        print(f"  - chunks.json ({os.path.getsize(chunks_path) / 1024:.1f} KB)")
        print(f"  - index_info.json")

        return output_dir


def main():
    """Главная функция."""
    import sys

    # Пути - используем абсолютные пути или относительно скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    knowledge_base_dir = os.path.join(project_root, "Task2", "knowledge_base")
    output_dir = os.path.join(script_dir, "index_output")

    # Проверить наличие базы знаний
    if not os.path.exists(knowledge_base_dir):
        print(f"❌ Директория базы знаний не найдена: {knowledge_base_dir}")
        print("Пожалуйста, сначала выполните Task 2")
        sys.exit(1)

    print("=" * 60)
    print("Задание 3: Создание векторного индекса")
    print("=" * 60)

    # Инициализировать индексер
    print("\n1. Загрузка модели эмбеддингов...")
    indexer = KnowledgeBaseIndexer(
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Загрузить документы
    print("\n2. Загрузка документов...")
    documents = indexer.load_documents(knowledge_base_dir)

    # Разбить на чанки
    print("\n3. Разбиение на чанки...")
    chunks = indexer.chunk_documents(documents)

    # Сгенерировать эмбеддинги
    print("\n4. Генерирование эмбеддингов...")
    embeddings = indexer.generate_embeddings()

    # Построить индекс
    print("\n5. Построение FAISS индекса...")
    index = indexer.build_index()

    # Сохранить результаты
    print("\n6. Сохранение индекса...")
    print(f"  Сохранение в: {output_dir}")
    print(f"  Script dir: {script_dir}")
    print(f"  CWD: {os.getcwd()}")
    indexer.save_index(output_dir)

    # Тестирование
    print("\n7. Тестирование поиска...")
    test_queries = [
        "Вакүм Ядро и ее мощь",
        "Кто был лидером Свободного Альянса",
        "Как работает Синтез Поток",
    ]

    for query in test_queries[:1]:  # Тестируем один запрос
        print(f"\nЗапрос: '{query}'")
        results = indexer.search(query, k=3)
        print(f"Результаты (3 лучших):")
        for i, result in enumerate(results, 1):
            preview = result["text"][:100] + "..."
            print(f"  {i}. [{result['source']}] Distance: {result['distance']:.4f}")
            print(f"     {preview}")

    print("\n" + "=" * 60)
    print("✓ Задание 3 завершено")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Ensure proper cleanup of multiprocessing resources
        import gc
        gc.collect()

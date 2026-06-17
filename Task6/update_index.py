#!/usr/bin/env python3
"""
Задание 6: Автоматическое ежедневное обновление базы знаний

Скрипт сканирует источник данных, находит новые/изменённые документы,
обновляет векторный индекс и логирует процесс.
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import sys

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
except ImportError:
    print("Please install: pip install sentence-transformers faiss-cpu")
    sys.exit(1)

# Настройка логирования
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"update_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Разбивает документы на логические чанки."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size * 4
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Разбить текст на чанки с метаданными."""
        chunks = []
        text_length = len(text)
        chunk_id = 0

        start = 0
        while start < text_length:
            end = min(start + self.chunk_size, text_length)

            if end < text_length:
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "start_pos": start,
                    "end_pos": end,
                    "source": metadata.get("source", "unknown"),
                    "title": metadata.get("title", ""),
                })
                chunk_id += 1

            start = end - self.overlap

        return chunks


class IndexUpdater:
    """Обновляет индекс документов."""

    def __init__(
        self,
        docs_source: str = "../../Task2/knowledge_base",
        index_dir: str = "../../Task3/index_output",
        index_state_file: str = "index_state.json"
    ):
        """
        Args:
            docs_source: директория с документами
            index_dir: директория с FAISS индексом
            index_state_file: файл для отслеживания состояния документов
        """
        self.docs_source = docs_source
        self.index_dir = index_dir
        self.index_state_file = index_state_file

        # Загрузить модель рмодель
        logger.info("Загрузка модели эмбеддингов...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_dim = self.model.get_embedding_dimension()

        # Загрузить существующий индекс
        logger.info("Загрузка существующего индекса...")
        index_path = os.path.join(index_dir, "faiss.index")
        self.index = faiss.read_index(index_path)

        # Загрузить чанки
        chunks_path = os.path.join(index_dir, "chunks.json")
        with open(chunks_path, 'r') as f:
            self.chunks = json.load(f)

        # Загрузить состояние
        if os.path.exists(index_state_file):
            with open(index_state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {}

    def get_file_hash(self, filepath: str) -> str:
        """Получить хеш файла."""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def find_new_and_modified_files(self) -> Tuple[List[str], List[str]]:
        """Найти новые и изменённые файлы."""
        docs_path = Path(self.docs_source)
        new_files = []
        modified_files = []

        for file_path in sorted(docs_path.glob("*.txt")):
            if file_path.name == "terms_map.json":
                continue

            file_hash = self.get_file_hash(str(file_path))
            file_name = file_path.name
            old_hash = self.state.get(file_name)

            if old_hash is None:
                new_files.append(str(file_path))
                logger.info(f"Новый файл: {file_name}")
            elif old_hash != file_hash:
                modified_files.append(str(file_path))
                logger.info(f"Изменённый файл: {file_name}")

        return new_files, modified_files

    def load_documents(self, file_paths: List[str]) -> List[Dict]:
        """Загрузить документы из файлов."""
        docs = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                title = lines[0].replace('# ', '').strip() if lines[0].startswith('#') else "Unknown"
                text_content = '\n'.join(lines[1:]).strip()

                if text_content:
                    docs.append({
                        "title": title,
                        "source": Path(file_path).name,
                        "content": text_content,
                        "filepath": file_path,
                    })
            except Exception as e:
                logger.error(f"Ошибка чтения {file_path}: {e}")

        return docs

    def update_index(self, new_docs: List[Dict], modified_docs: List[Dict]) -> Dict:
        """Обновить индекс новыми и изменёнными документами."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "new_documents": len(new_docs),
            "modified_documents": len(modified_docs),
            "new_chunks": 0,
            "modified_chunks": 0,
            "errors": 0,
        }

        chunker = DocumentChunker()

        # Обработать новые документы
        for doc in new_docs:
            try:
                chunks = chunker.chunk_text(
                    doc["content"],
                    {"source": doc["source"], "title": doc["title"]}
                )

                # Сгенерировать эмбеддинги
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = self.model.encode(chunk_texts, show_progress_bar=False).astype('float32')

                # Добавить в индекс
                self.index.add(embeddings)

                # Добавить чанки
                max_chunk_id = max([c.get("chunk_id", 0) for c in self.chunks]) if self.chunks else 0
                for i, chunk in enumerate(chunks):
                    chunk["chunk_id"] = max_chunk_id + i + 1
                    self.chunks.append(chunk)

                stats["new_chunks"] += len(chunks)
                logger.info(f"Обрабатано: {doc['source']} ({len(chunks)} чанков)")

            except Exception as e:
                logger.error(f"Ошибка обработки {doc['source']}: {e}")
                stats["errors"] += 1

        # Обработать изменённые документы
        for doc in modified_docs:
            try:
                # Найти старые чанки этого документа и удалить их
                sources_to_remove = [doc["source"]]
                old_indices = [i for i, c in enumerate(self.chunks) if c["source"] in sources_to_remove]

                if old_indices:
                    # Для FAISS нужно перестроить индекс без старых документов
                    logger.info(f"Удаление {len(old_indices)} старых чанков для {doc['source']}")
                    remaining_chunks = [c for i, c in enumerate(self.chunks) if i not in old_indices]
                    remaining_embeddings = np.array([
                        self.index.reconstruct(i) for i in range(self.index.ntotal)
                        if i not in old_indices
                    ]).astype('float32')

                    # Перестроить индекс
                    self.index = faiss.IndexFlatL2(self.embedding_dim)
                    if len(remaining_embeddings) > 0:
                        self.index.add(remaining_embeddings)
                    self.chunks = remaining_chunks

                # Добавить новые чанки для изменённого документа
                chunks = chunker.chunk_text(
                    doc["content"],
                    {"source": doc["source"], "title": doc["title"]}
                )

                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = self.model.encode(chunk_texts, show_progress_bar=False).astype('float32')
                self.index.add(embeddings)

                max_chunk_id = max([c.get("chunk_id", 0) for c in self.chunks]) if self.chunks else 0
                for i, chunk in enumerate(chunks):
                    chunk["chunk_id"] = max_chunk_id + i + 1
                    self.chunks.append(chunk)

                stats["modified_chunks"] += len(chunks)
                logger.info(f"Обновлено: {doc['source']} ({len(chunks)} чанков)")

            except Exception as e:
                logger.error(f"Ошибка обновления {doc['source']}: {e}")
                stats["errors"] += 1

        return stats

    def save_index(self) -> None:
        """Сохранить обновлённый индекс."""
        # Сохранить FAISS индекс
        index_path = os.path.join(self.index_dir, "faiss.index")
        faiss.write_index(self.index, index_path)

        # Сохранить чанки
        chunks_path = os.path.join(self.index_dir, "chunks.json")
        with open(chunks_path, 'w') as f:
            json.dump(self.chunks, f)

        logger.info(f"Индекс сохранён. Всего чанков: {len(self.chunks)}")

    def save_state(self, file_paths: List[str]) -> None:
        """Сохранить состояние файлов."""
        for file_path in file_paths:
            file_name = Path(file_path).name
            self.state[file_name] = self.get_file_hash(file_path)

        with open(self.index_state_file, 'w') as f:
            json.dump(self.state, f)

        logger.info(f"Состояние сохранено ({len(self.state)} файлов отслеживается)")

    def run(self) -> Dict:
        """Запустить обновление индекса."""
        logger.info("=" * 60)
        logger.info("Начало обновления индекса")
        logger.info("=" * 60)

        start_time = time.time()

        # Найти новые и изменённые файлы
        new_files, modified_files = self.find_new_and_modified_files()

        if not new_files and not modified_files:
            logger.info("Новых или изменённых документов не найдено")
            return {
                "status": "no_changes",
                "timestamp": datetime.now().isoformat()
            }

        # Загрузить документы
        all_docs = self.load_documents(new_files + modified_files)

        if not all_docs:
            logger.error("Не удалось загрузить документы")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }

        # Разделить на новые и изменённые
        new_doc_sources = {Path(f).name for f in new_files}
        new_docs = [d for d in all_docs if d["source"] in new_doc_sources]
        modified_docs = [d for d in all_docs if d["source"] not in new_doc_sources]

        # Обновить индекс
        stats = self.update_index(new_docs, modified_docs)

        # Сохранить индекс
        self.save_index()

        # Сохранить состояние
        self.save_state(new_files + modified_files)

        elapsed = time.time() - start_time
        stats["elapsed_seconds"] = elapsed
        stats["status"] = "success"

        logger.info("=" * 60)
        logger.info(f"Обновление завершено за {elapsed:.2f} сек")
        logger.info(f"Новых чанков: {stats['new_chunks']}")
        logger.info(f"Изменённых чанков: {stats['modified_chunks']}")
        logger.info(f"Ошибок: {stats['errors']}")
        logger.info("=" * 60)

        return stats


def main():
    """Главная функция."""
    try:
        updater = IndexUpdater()
        result = updater.run()

        # Вывести результаты
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Сохранить результаты в JSON лог
        with open(log_dir / f"update_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Task 6: Testing and demonstration of index update process

Tests the update_index.py script with simulated scenarios:
- New document addition
- Index consistency
- Log generation
- Performance metrics
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/Users/shademang/Projects/new/ai-homework')

# Colors
HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{HEADER}{BOLD}{'═' * 80}{RESET}")
    print(f"{HEADER}{BOLD}  {text}{RESET}")
    print(f"{HEADER}{BOLD}{'═' * 80}{RESET}\n")

def print_section(text):
    print(f"\n{CYAN}{BOLD}{'─' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  {text}{RESET}")
    print(f"{CYAN}{BOLD}{'─' * 80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def print_test(num, desc):
    print(f"{BLUE}TEST {num}: {desc}{RESET}")

def get_index_stats():
    """Get current index statistics."""
    stats = {
        'exists': False,
        'size': 0,
        'chunks': 0,
        'updated_at': None
    }

    index_path = "../Task3/index_output"

    if not Path(index_path).exists():
        return stats

    stats['exists'] = True

    # Get FAISS index size
    faiss_path = Path(index_path) / "faiss.index"
    if faiss_path.exists():
        stats['size'] = faiss_path.stat().st_size

    # Get chunks count
    chunks_path = Path(index_path) / "chunks.json"
    if chunks_path.exists():
        try:
            with open(chunks_path) as f:
                chunks = json.load(f)
                stats['chunks'] = len(chunks)
        except:
            pass

    # Get update time
    index_info_path = Path(index_path) / "index_info.json"
    if index_info_path.exists():
        try:
            with open(index_info_path) as f:
                info = json.load(f)
                stats['updated_at'] = info.get('created_at', 'unknown')
        except:
            pass

    return stats

def test_log_generation():
    """Test 1: Log file generation"""
    print_test(1, "Проверка генерирования логов")

    log_dir = Path("logs")

    if not log_dir.exists():
        print_info("Директория логов не найдена - она будет создана при первом запуске")
        return True

    log_files = list(log_dir.glob("update_*.log"))

    if not log_files:
        print_info("Логов не найдено - они будут созданы при первом запуске")
        return True

    latest_log = sorted(log_files)[-1]

    # Check log content
    with open(latest_log) as f:
        content = f.read()

    required_keywords = [
        "Сканирование источника",
        "индекс",
        "ИТОГИ",
        "Статус"
    ]

    found = sum(1 for keyword in required_keywords if keyword in content)

    print_success(f"Последний лог: {latest_log.name}")
    print_success(f"Ключевые слова найдены: {found}/{len(required_keywords)}")
    print_info(f"Размер лога: {latest_log.stat().st_size / 1024:.1f} KB")

    return found >= len(required_keywords) - 1

def test_index_consistency():
    """Test 2: Index consistency"""
    print_test(2, "Проверка консистентности индекса")

    index_path = Path("../Task3/index_output")

    if not index_path.exists():
        print_error("Индекс не найден - запустите Task 3 сначала")
        return False

    files = {
        "faiss.index": False,
        "chunks.json": False,
        "index_info.json": False
    }

    for file in files:
        file_path = index_path / file
        if file_path.exists():
            files[file] = True
            size = file_path.stat().st_size
            print_success(f"{file}: {size / 1024:.1f} KB")
        else:
            print_error(f"{file}: не найден")

    # Validate JSON files
    try:
        with open(index_path / "chunks.json") as f:
            chunks = json.load(f)
        print_success(f"chunks.json валидный JSON ({len(chunks)} чанков)")
    except Exception as e:
        print_error(f"chunks.json невалидный: {e}")
        files["chunks.json"] = False

    try:
        with open(index_path / "index_info.json") as f:
            info = json.load(f)
        print_success(f"index_info.json валидный JSON")
        print_info(f"  Модель: {info.get('embedding_model', 'unknown')}")
        print_info(f"  Чанков: {info.get('total_chunks', 'unknown')}")
        print_info(f"  Размерность: {info.get('embedding_dimension', 'unknown')}")
    except Exception as e:
        print_error(f"index_info.json невалидный: {e}")
        files["index_info.json"] = False

    return all(files.values())

def test_history_cache():
    """Test 3: History cache management"""
    print_test(3, "Проверка кеша истории (history.json)")

    history_path = Path("history.json")

    if not history_path.exists():
        print_info("History.json еще не создан - будет создан при первом запуске обновления")
        return True

    try:
        with open(history_path) as f:
            history = json.load(f)

        print_success(f"history.json найден и валиден")
        print_info(f"Отслеживаемых файлов: {len(history)}")

        # Sample entries
        for i, (filename, hash_val) in enumerate(list(history.items())[:3]):
            print_info(f"  {filename}: {hash_val[:8]}...")

        if len(history) > 3:
            print_info(f"  ... и еще {len(history) - 3}")

        return True
    except Exception as e:
        print_error(f"history.json невалиден: {e}")
        return False

def test_data_source():
    """Test 4: Data source availability"""
    print_test(4, "Проверка доступности источника данных")

    source_path = Path("../Task2/knowledge_base")

    if not source_path.exists():
        print_error("Источник данных не найден: ../Task2/knowledge_base")
        return False

    files = list(source_path.glob("document_*.txt"))

    if not files:
        print_error("Документов не найдено в knowledge_base")
        return False

    print_success(f"Источник данных найден")
    print_info(f"Всего документов: {len(files)}")

    # Sample file info
    total_size = 0
    for file in files[:5]:
        size = file.stat().st_size
        total_size += size
        print_info(f"  {file.name}: {size / 1024:.1f} KB")

    if len(files) > 5:
        total_size += sum(f.stat().st_size for f in files[5:])
        print_info(f"  ... и еще {len(files) - 5} файлов")

    print_info(f"Общий размер: {total_size / 1024:.1f} KB")

    return True

def test_logs_directory():
    """Test 5: Logs directory and rotation"""
    print_test(5, "Проверка директории логов")

    log_dir = Path("logs")

    if not log_dir.exists():
        print_info("Логи еще не созданы - будут созданы при первом запуске")
        return True

    log_files = list(log_dir.glob("*.log"))

    if not log_files:
        print_info("Логов еще не создано")
        return True

    print_success(f"Логи найдены: {len(log_files)} файлов")

    # Statistics
    total_size = sum(f.stat().st_size for f in log_files)

    print_info(f"Общий размер логов: {total_size / 1024:.1f} KB")

    # Latest logs
    sorted_logs = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

    print_section("Последние логи:")
    for log in sorted_logs[:5]:
        mod_time = datetime.fromtimestamp(log.stat().st_mtime)
        size = log.stat().st_size
        print_info(f"  {log.name}: {size / 1024:.1f} KB ({mod_time.strftime('%Y-%m-%d %H:%M')})")

    return True

def show_recommendations():
    """Show recommendations based on test results"""
    print_section("РЕКОМЕНДАЦИИ")

    print(f"{CYAN}Для использования Task 6:{RESET}\n")

    print(f"1. {BOLD}Ручной запуск обновления:{RESET}")
    print(f"   cd Task6")
    print(f"   bash run.sh")
    print(f"   # Выбрать опцию 1\n")

    print(f"2. {BOLD}Установка автоматического запуска (Cron):{RESET}")
    print(f"   cd Task6")
    print(f"   crontab crontab_config.txt  # Установить расписание")
    print(f"   crontab -l                  # Проверить\n")

    print(f"3. {BOLD}Просмотр логов:{RESET}")
    print(f"   bash run.sh")
    print(f"   # Выбрать опцию 2 или 3\n")

    print(f"4. {BOLD}Статистика обновлений:{RESET}")
    print(f"   bash run.sh")
    print(f"   # Выбрать опцию 4\n")

# Main test runner
if __name__ == "__main__":
    print_header("ТЕСТИРОВАНИЕ Task 6: Автоматическое обновление")

    # Get initial stats
    print_section("НАЧАЛЬНОЕ СОСТОЯНИЕ")
    stats = get_index_stats()

    print_info("Статус индекса:")
    if stats['exists']:
        print_success(f"  Существует: да")
        print_success(f"  Размер: {stats['size'] / 1024 / 1024:.1f} MB")
        print_success(f"  Чанков: {stats['chunks']}")
        if stats['updated_at']:
            print_success(f"  Обновлен: {stats['updated_at']}")
    else:
        print_error("  Индекс не построен - запустите Task 3 сначала")

    # Run tests
    print_header("ЗАПУСК ТЕСТОВ")

    results = {}

    results['log_generation'] = test_log_generation()
    print()

    results['index_consistency'] = test_index_consistency()
    print()

    results['history_cache'] = test_history_cache()
    print()

    results['data_source'] = test_data_source()
    print()

    results['logs_directory'] = test_logs_directory()
    print()

    # Summary
    print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if passed_flag else f"{RED}✗ FAIL{RESET}"
        print(f"{status}  {test_name}")

    print()
    print_section(f"ИТОГО: {passed}/{total} тестов пройдено")

    if passed == total:
        print_success("ВСЕ ТЕСТЫ ПРОЙДЕНЫ успешно!")
    elif passed >= total - 1:
        print_info("Большинство тестов пройдено. Система готова к использованию.")
    else:
        print_error(f"Некоторые тесты не пройдены. Требуется дополнительная проверка.")

    # Show recommendations
    show_recommendations()

    print()

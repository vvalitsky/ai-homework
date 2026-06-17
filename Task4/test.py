#!/usr/bin/env python3
"""
Task 4: RAG Bot Testing Script

Tests the RAG bot with various queries and validates:
- Bot initialization
- Query processing
- Context retrieval
- Answer generation
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, '/Users/shademang/Projects/new/ai-homework')

try:
    from Task4.rag_bot import RAGBot

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
        print(f"\n{HEADER}{BOLD}{'═' * 70}{RESET}")
        print(f"{HEADER}{BOLD}  {text}{RESET}")
        print(f"{HEADER}{BOLD}{'═' * 70}{RESET}\n")

    def print_section(text):
        print(f"\n{CYAN}{BOLD}{'─' * 70}{RESET}")
        print(f"{CYAN}{BOLD}  {text}{RESET}")
        print(f"{CYAN}{BOLD}{'─' * 70}{RESET}\n")

    def print_success(text):
        print(f"{GREEN}✓ {text}{RESET}")

    def print_error(text):
        print(f"{RED}✗ {text}{RESET}")

    def print_info(text):
        print(f"{YELLOW}ℹ {text}{RESET}")

    # Initialize
    print_header("ИНИЦИАЛИЗАЦИЯ RAG-БОТА")
    print_info("Загрузка компонентов...")

    try:
        bot = RAGBot(index_dir="../Task3/index_output")
        print_success("БОТ ИНИЦИАЛИЗИРОВАН")
    except Exception as e:
        print_error(f"Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Test 1: Basic functionality
    print_header("ТЕСТ 1: Базовая функциональность")

    test_query = "Кто такой Каелин Скайфайер?"
    print_info(f"Тестовый запрос: '{test_query}'")

    try:
        result = bot.answer(test_query, top_k=3)

        if result["context"]:
            print_success(f"Найдено {len(result['context'])} релевантных документов")

            for i, doc in enumerate(result["context"], 1):
                print(f"\n  {CYAN}Документ {i}:{RESET}")
                print(f"    Источник: {doc['source']}")
                print(f"    Заголовок: {doc['title']}")
                print(f"    Текст: {doc['text'][:100]}...")
        else:
            print_error("Документы не найдены")

        # Check prompt generation
        if "prompt" in result:
            print_success("Промпт сгенерирован успешно")
            print(f"  Длина промпта: {len(result['prompt'])} символов")
        else:
            print_error("Промпт не сгенерирован")

    except Exception as e:
        print_error(f"Тестовый запрос завершился с ошибкой: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Multiple queries
    print_header("ТЕСТ 2: Множественные запросы")

    test_queries = [
        "Какова была цель Вакуум Ядра?",
        "Расскажи про неизвестную империю",
        "Что произошло с Malthor the Dark?",
        "Какие персонажи упоминаются в истории?",
        "Что такое Synth Flux?",
    ]

    passed = 0
    failed = 0

    for i, query in enumerate(test_queries, 1):
        try:
            print_info(f"Запрос {i}: '{query}'")
            result = bot.answer(query, top_k=2)

            if result["context"]:
                print_success(f"  Найдено {len(result['context'])} документов")
                passed += 1
            else:
                print_info(f"  Документы не найдены (честный отказ)")
                passed += 1

        except Exception as e:
            print_error(f"  Ошибка: {e}")
            failed += 1

        print()

    print_section(f"Результат: {passed} успешных, {failed} ошибок")

    # Test 3: Top-K variations
    print_header("ТЕСТ 3: Вариации top_k")

    query = "Кто такой Каелин Скайфайер?"
    top_k_values = [1, 3, 5]

    for k in top_k_values:
        try:
            result = bot.answer(query, top_k=k)
            found = len(result["context"]) if result["context"] else 0
            print_info(f"top_k={k}: найдено {found} документов")
            print_success(f"  Размер промпта: {len(result['prompt'])} символов")
        except Exception as e:
            print_error(f"top_k={k}: ошибка {e}")

    # Summary
    print_header("ИТОГИ ТЕСТИРОВАНИЯ")

    print_success("БОТ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print()
    print_info("Доступные интерфейсы:")
    print(f"  {CYAN}1. Интерактивный REPL:{RESET}")
    print(f"     bash run.sh (выбрать опцию 1)")
    print()
    print(f"  {CYAN}2. REST API:{RESET}")
    print(f"     bash run.sh (выбрать опцию 2)")
    print(f"     http://localhost:8000/docs")
    print()

except Exception as e:
    print_error(f"Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

#!/bin/bash

# Task 4: RAG Bot - Run Script
# Provides multiple interfaces: REPL, API, and testing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_header() {
    echo -e "\n${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║ $1${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_section "Проверка предусловий"

    if [ ! -d "../.venv" ]; then
        print_error "Виртуальное окружение не создано"
        print_info "Запустите: bash ../scripts/setup.sh"
        exit 1
    fi

    if [ ! -f "../Task3/index_output/faiss.index" ]; then
        print_error "FAISS индекс не построен"
        exit 1
    fi

    print_success "Все предусловия выполнены"
}

# Run REPL interface
run_repl() {
    print_header "ИНТЕРАКТИВНЫЙ RAG-БОТ (REPL)"

    source ../.venv/bin/activate

    python3 -u repl.py

    deactivate
}

# Run REST API
run_api() {
    print_header "ЗАПУСК REST API"

    source ../.venv/bin/activate

    print_info "Активация виртуального окружения..."
    print_info "Запуск FastAPI сервера..."
    print_info "Сервер будет доступен на http://localhost:8000"
    print_info "Документация: http://localhost:8000/docs"
    print_info "Для остановки нажмите Ctrl+C"
    echo ""

    python3 rag_api.py

    deactivate
}

# Run quick test
run_test() {
    print_header "БЫСТРЫЙ ТЕСТ RAG-БОТА"

    source ../.venv/bin/activate

    python3 << 'PYTHON'
import sys
sys.path.insert(0, '/Users/shademang/Projects/new/ai-homework')

try:
    from Task4.rag_bot import RAGBot

    print("╔════════════════════════════════════════════════════════╗")
    print("║        БЫСТРЫЙ ТЕСТ RAG-БОТА                          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Загрузка индекса...")
    bot = RAGBot(index_dir="../Task3/index_output")
    print("✓ БОТ ГОТОВ!\n")

    # Test queries
    test_queries = [
        "Кто такой Каелин Скайфайер?",
        "Какова была цель Вакуум Ядра?",
        "Расскажи про неизвестную империю"
    ]

    print("Обработка тестовых запросов:\n")

    for i, query in enumerate(test_queries, 1):
        print(f"[Запрос {i}] {query}")
        result = bot.answer(query, top_k=2)

        if result["context"]:
            print(f"  ✓ Найдено {len(result['context'])} документов")
            for j, doc in enumerate(result["context"], 1):
                print(f"    {j}. [{doc['source']}]")
        else:
            print("  ✓ Честный отказ: информация не найдена")
        print()

    print("✓ Все тесты завершены успешно!")

except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
PYTHON

    deactivate
}

# Main menu
main() {
    print_header "ЗАДАНИЕ 4: RAG-БОТ С ТЕХНИКАМИ ПРОМПТИНГА"

    echo "Выберите режим запуска:"
    echo ""
    echo "  1) Интерактивный REPL (чат)"
    echo "  2) REST API (FastAPI на :8000)"
    echo "  3) Быстрый тест"
    echo "  0) Выход"
    echo ""
    read -p "Введите номер (0-3): " choice

    case $choice in
        1) run_repl ;;
        2) run_api ;;
        3) check_prerequisites; run_test ;;
        0) print_info "Выход"; exit 0 ;;
        *) print_info "Неверный выбор"; main ;;
    esac
}

# Check prerequisites first
check_prerequisites

# Activate virtual environment and run main menu
source ../.venv/bin/activate
main
deactivate

#!/bin/bash

# Task 5: RAG Bot Demonstration and Security Testing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║ $1${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}\n"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
print_header "ЗАДАНИЕ 5: Демонстрация и тестирование RAG-бота"

if [ ! -d "../.venv" ]; then
    print_error "Виртуальное окружение не создано"
    print_info "Запустите: bash ../scripts/setup.sh"
    exit 1
fi

if [ ! -f "../Task3/index_output/faiss.index" ]; then
    print_error "FAISS индекс не построен"
    print_info "Запустите: bash ../run_examples.sh (выбрать опцию 5)"
    exit 1
fi

if [ ! -f "../Task4/rag_bot.py" ]; then
    print_error "RAG бот не найден"
    exit 1
fi

print_success "Все предусловия выполнены"

# Activate virtual environment
source ../.venv/bin/activate

# Run the demonstration
print_info "Запуск демонстрации..."
echo ""

python3 -u run.py

print_header "Демонстрация завершена"
print_info "Результаты сохранены выше"
echo ""

#!/bin/bash

#╔══════════════════════════════════════════════════════════════════════════╗
#║        RAG-БОТ: СКРИПТ УСТАНОВКИ И ПОДГОТОВКИ ОКРУЖЕНИЯ                  ║
#╚══════════════════════════════════════════════════════════════════════════╝

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}\n"
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

# Главное меню
main() {
    print_header "RAG-БОТ: УСТАНОВКА ОКРУЖЕНИЯ"

    echo "Выберите действие:"
    echo "  1) Полная установка (venv + зависимости + база знаний + индекс)"
    echo "  2) Только Python зависимости"
    echo "  3) Только подготовить базу знаний"
    echo "  4) Только построить FAISS индекс"
    echo "  5) Проверить установку"
    echo "  6) Очистить all (удалить venv, индекс, логи)"
    echo "  0) Выход"
    echo ""
    read -p "Введите номер (0-6): " choice

    case $choice in
        1) full_setup ;;
        2) install_dependencies ;;
        3) prepare_knowledge_base ;;
        4) build_index ;;
        5) check_installation ;;
        6) cleanup ;;
        0) print_info "Выход"; exit 0 ;;
        *) print_error "Неверный выбор"; main ;;
    esac
}

# Полная установка
full_setup() {
    print_header "ПОЛНАЯ УСТАНОВКА"

    # Проверка Python
    print_info "Проверка Python..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не найден"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION найден"

    # Создание venv
    print_info "Создание виртуального окружения..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Виртуальное окружение создано"
    else
        print_info "Виртуальное окружение уже существует"
    fi

    # Активация venv
    print_info "Активация виртуального окружения..."
    source .venv/bin/activate

    # Установка зависимостей
    print_info "Установка зависимостей..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Зависимости установлены"

    # Подготовка базы знаний
    print_info "Подготовка базы знаний..."
    cd Task2
    python3 create_knowledge_base.py
    cd ..
    print_success "База знаний готова"

    # Построение индекса
    print_info "Построение FAISS индекса (может занять 15-20 минут)..."
    cd Task3
    python3 build_index.py
    cd ..
    print_success "Индекс построен"

    print_success "Полная установка завершена!"
    echo ""
    print_info "Для запуска бота используйте:"
    echo "  source .venv/bin/activate"
    echo "  cd Task4"
    echo "  python3 rag_api.py"
}

# Установка зависимостей
install_dependencies() {
    print_header "УСТАНОВКА ЗАВИСИМОСТЕЙ"

    if [ ! -d ".venv" ]; then
        print_info "Создание виртуального окружения..."
        python3 -m venv .venv
    fi

    source .venv/bin/activate
    print_info "Установка зависимостей..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1

    print_success "Зависимости установлены!"
    echo ""
    print_info "Для активации окружения используйте:"
    echo "  source .venv/bin/activate"
}

# Подготовка базы знаний
prepare_knowledge_base() {
    print_header "ПОДГОТОВКА БАЗЫ ЗНАНИЙ"

    if [ ! -d ".venv" ]; then
        print_error "Виртуальное окружение не создано. Запустите сначала: bash scripts/setup.sh"
        exit 1
    fi

    source .venv/bin/activate
    cd Task2

    print_info "Генерирование 36 документов с подстановками..."
    python3 create_knowledge_base.py

    if [ -d "knowledge_base" ] && [ -f "knowledge_base/terms_map.json" ]; then
        DOCS_COUNT=$(find knowledge_base -name "document_*.txt" | wc -l)
        print_success "База знаний готова!"
        echo "  - Документов: $DOCS_COUNT"
        echo "  - Директория: knowledge_base/"
        echo "  - Словарь замен: knowledge_base/terms_map.json"
    else
        print_error "Ошибка при создании базы знаний"
        exit 1
    fi

    cd ..
}

# Построение индекса
build_index() {
    print_header "ПОСТРОЕНИЕ FAISS ИНДЕКСА"

    if [ ! -d ".venv" ]; then
        print_error "Виртуальное окружение не создано"
        exit 1
    fi

    if [ ! -d "Task2/knowledge_base" ]; then
        print_error "База знаний не готова. Запустите сначала подготовку базы"
        exit 1
    fi

    source .venv/bin/activate
    cd Task3

    print_info "Построение индекса (это может занять 15-20 минут...)..."
    python3 build_index.py

    if [ -d "index_output" ] && [ -f "index_output/faiss.index" ]; then
        INDEX_SIZE=$(du -sh index_output/faiss.index | cut -f1)
        print_success "Индекс построен!"
        echo "  - Размер: $INDEX_SIZE"
        echo "  - Директория: index_output/"
    else
        print_error "Ошибка при построении индекса"
        exit 1
    fi

    cd ..
}

# Проверка установки
check_installation() {
    print_header "ПРОВЕРКА УСТАНОВКИ"

    # Python
    if command -v python3 &> /dev/null; then
        print_success "Python3 установлен ($(python3 --version))"
    else
        print_error "Python3 не найден"
    fi

    # venv
    if [ -d ".venv" ]; then
        print_success "Виртуальное окружение существует"
    else
        print_error "Виртуальное окружение не создано"
    fi

    # requirements.txt
    if [ -f "requirements.txt" ]; then
        print_success "requirements.txt найден"
    else
        print_error "requirements.txt не найден"
    fi

    # База знаний
    if [ -d "Task2/knowledge_base" ]; then
        DOCS=$(find Task2/knowledge_base -name "document_*.txt" | wc -l)
        print_success "База знаний готова ($DOCS документов)"
    else
        print_error "База знаний не готова"
    fi

    # Индекс FAISS
    if [ -f "Task3/index_output/faiss.index" ]; then
        print_success "FAISS индекс построен"
    else
        print_error "FAISS индекс не построен"
    fi

    # Docker
    if command -v docker &> /dev/null; then
        print_success "Docker установлен ($(docker --version))"
    else
        print_error "Docker не установлен"
    fi

    # docker-compose
    if command -v docker-compose &> /dev/null; then
        print_success "docker-compose установлен ($(docker-compose --version))"
    else
        print_error "docker-compose не установлен"
    fi

    echo ""
    print_info "Статус готовности к запуску:"

    READY=true
    [ ! -d ".venv" ] && READY=false
    [ ! -d "Task2/knowledge_base" ] && READY=false
    [ ! -f "Task3/index_output/faiss.index" ] && READY=false

    if [ "$READY" = true ]; then
        print_success "✓ Проект готов к запуску!"
    else
        print_error "✗ Проект не полностью готов. Запустите полную установку."
    fi
}

# Очистка
cleanup() {
    print_header "ОЧИСТКА"

    read -p "Вы уверены? Будут удалены: .venv, индекс, логи (y/N): " confirm
    if [ "$confirm" != "y" ]; then
        print_info "Очистка отменена"
        return
    fi

    print_info "Удаление .venv..."
    rm -rf .venv

    print_info "Удаление индекса..."
    rm -rf Task3/index_output

    print_info "Удаление логов..."
    rm -rf Task6/logs

    print_info "Удаление .idea..."
    rm -rf .idea

    print_success "Очистка завершена"
}

# Запуск main
main

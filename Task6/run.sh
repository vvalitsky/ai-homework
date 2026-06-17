#!/bin/bash

# Task 6: Automatic Daily Knowledge Base Update
# Provides interfaces for updating the index, viewing logs, and managing scheduled tasks

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

    if [ ! -f "update_index.py" ]; then
        print_error "Скрипт update_index.py не найден"
        exit 1
    fi

    print_success "Все предусловия выполнены"
}

# Run index update
run_update() {
    print_header "ОБНОВЛЕНИЕ ИНДЕКСА"

    source ../.venv/bin/activate

    print_info "Запуск скрипта обновления..."
    python3 -u update_index.py

    deactivate

    print_success "Обновление завершено!"
}

# View logs
view_logs() {
    print_header "ПРОСМОТР ЛОГОВ"

    if [ ! -d "logs" ]; then
        print_error "Директория логов не найдена"
        return
    fi

    print_section "Доступные логи:"

    ls -lh logs/ 2>/dev/null | tail -n +2

    echo ""
    read -p "Введите имя файла лога для просмотра (или Enter для выхода): " log_file

    if [ -z "$log_file" ]; then
        return
    fi

    if [ -f "logs/$log_file" ]; then
        print_section "Содержание логов/$log_file"
        cat "logs/$log_file"
    else
        print_error "Файл не найден"
    fi
}

# View latest log
view_latest_log() {
    print_header "ПОСЛЕДНИЙ ЛОГ"

    if [ ! -d "logs" ]; then
        print_error "Директория логов не найдена"
        return
    fi

    latest_log=$(ls -t logs/*.log 2>/dev/null | head -1)

    if [ -z "$latest_log" ]; then
        print_error "Логи не найдены"
        return
    fi

    print_info "Файл: $latest_log"
    echo ""
    tail -50 "$latest_log"
}

# View statistics
view_stats() {
    print_header "СТАТИСТИКА ОБНОВЛЕНИЙ"

    if [ ! -d "logs" ]; then
        print_error "Директория логов не найдена"
        return
    fi

    print_section "Общая статистика:"

    echo "Всего логов: $(ls logs/*.log 2>/dev/null | wc -l)"
    echo ""

    print_section "Последние 5 обновлений:"

    if [ -f "../Task3/index_output/index_info.json" ]; then
        echo "Текущее состояние индекса:"
        python3 << 'PYTHON'
import json
try:
    with open("../Task3/index_output/index_info.json") as f:
        info = json.load(f)
        print(f"  - Модель: {info['embedding_model']}")
        print(f"  - Чанков: {info['total_chunks']}")
        print(f"  - Размерность: {info['embedding_dimension']}")
        print(f"  - Дата обновления: {info.get('created_at', 'неизвестна')}")
except Exception as e:
    print(f"  Ошибка: {e}")
PYTHON
    fi

    echo ""
    print_section "История логов:"

    ls -lhrt logs/*.log 2>/dev/null | awk '{print $9, "(" $5 ")"}' | tail -5
}

# Show cron configuration
show_cron_config() {
    print_header "КОНФИГУРАЦИЯ CRON"

    if [ -f "crontab_config.txt" ]; then
        cat crontab_config.txt
    else
        print_error "Файл конфигурации не найден"
    fi

    echo ""
    print_info "Для установки cron-задачи:"
    echo "  1) Отредактируйте crontab_config.txt если требуется"
    echo "  2) Запустите: crontab crontab_config.txt"
    echo "  3) Проверьте: crontab -l"
}

# Show architecture diagram
show_diagram() {
    print_header "АРХИТЕКТУРНАЯ ДИАГРАММА"

    if [ -f "architecture.md" ]; then
        cat architecture.md
    else
        print_info "Диаграмма будет создана после первого запуска"
    fi
}

# Main menu
main() {
    print_header "ЗАДАНИЕ 6: Автоматическое обновление базы знаний"

    echo "Выберите действие:"
    echo ""
    echo "  1) Запустить обновление индекса"
    echo "  2) Просмотреть последний лог"
    echo "  3) Просмотреть все логи"
    echo "  4) Статистика обновлений"
    echo "  5) Показать конфигурацию Cron"
    echo "  6) Показать архитектурную диаграмму"
    echo "  0) Выход"
    echo ""
    read -p "Введите номер (0-6): " choice

    case $choice in
        1) run_update; main ;;
        2) view_latest_log; main ;;
        3) view_logs; main ;;
        4) view_stats; main ;;
        5) show_cron_config; main ;;
        6) show_diagram; main ;;
        0) print_info "Выход"; exit 0 ;;
        *) print_info "Неверный выбор"; main ;;
    esac
}

# Run main
check_prerequisites
main
